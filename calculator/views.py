from decimal import Decimal

from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from .forms import DepreciationForm


def depreciation(request):
    """
    Calculadora de depreciación por Línea Recta.

    Fórmula: Depreciación anual = (Valor Inicial - Valor Salvamento) / Vida Útil

    Esta vista solo está disponible en la Versión 2 (FEATURE_CALCULATOR=True).
    """
    if not settings.FEATURE_CALCULATOR:
        raise Http404("Módulo no disponible en esta versión.")

    form = DepreciationForm(request.POST or None)
    result = None

    if request.method == "POST" and form.is_valid():
        initial = form.cleaned_data["initial_value"]
        life = form.cleaned_data["useful_life"]
        salvage = form.cleaned_data["salvage_value"]

        annual = (initial - salvage) / Decimal(life)
        annual = annual.quantize(Decimal("0.01"))

        # Tabla de depreciación año por año
        schedule = []
        book_value = initial
        for year in range(1, life + 1):
            book_value -= annual
            schedule.append(
                {
                    "year": year,
                    "depreciation": annual,
                    "accumulated": (annual * year).quantize(Decimal("0.01")),
                    "book_value": book_value.quantize(Decimal("0.01")),
                }
            )

        result = {
            "annual": annual,
            "depreciable_base": (initial - salvage).quantize(Decimal("0.01")),
            "schedule": schedule,
        }

    return render(
        request,
        "calculator/depreciation.html",
        {"form": form, "result": result},
    )
