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

        annual = ((initial - salvage) / Decimal(life)).quantize(Decimal("0.01"))

        # Tabla de depreciación año por año
        schedule = []
        book_value = initial
        accumulated = Decimal("0.00")

        for year in range(1, life + 1):
            # En el último año, ajustamos para que el valor en libros
            # coincida exactamente con el valor de salvamento
            if year == life:
                year_depreciation = (book_value - salvage).quantize(Decimal("0.01"))
            else:
                year_depreciation = annual

            book_value = (book_value - year_depreciation).quantize(Decimal("0.01"))
            accumulated = (accumulated + year_depreciation).quantize(Decimal("0.01"))

            schedule.append(
                {
                    "year": year,
                    "depreciation": year_depreciation,
                    "accumulated": accumulated,
                    "book_value": book_value,
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