from django import forms


class DepreciationForm(forms.Form):
    """Datos para el cálculo de depreciación por Línea Recta."""

    initial_value = forms.DecimalField(
        label="Valor Inicial (S/.)",
        min_value=0.01,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "input", "placeholder": "Ej: 10000", "step": "0.01"}
        ),
        error_messages={
            "min_value": "El valor inicial debe ser mayor a 0.",
            "max_digits": "El valor inicial es demasiado grande.",
        },
    )
    useful_life = forms.IntegerField(
        label="Vida Útil (años)",
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": "Ej: 5"}),
        error_messages={
            "min_value": "La vida útil debe ser al menos 1 año.",
            "max_value": "La vida útil no puede superar los 100 años.",
        },
    )
    salvage_value = forms.DecimalField(
        label="Valor de Salvamento (S/.)",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "input", "placeholder": "Ej: 1000", "step": "0.01"}
        ),
        error_messages={
            "min_value": "El valor de salvamento no puede ser negativo.",
            "max_digits": "El valor de salvamento es demasiado grande.",
        },
    )

    def clean(self):
        data = super().clean()
        initial = data.get("initial_value")
        salvage = data.get("salvage_value")

        if initial is not None and salvage is not None:
            if salvage > initial:
                raise forms.ValidationError(
                    "El valor de salvamento no puede ser mayor que el valor inicial."
                )
            if salvage == initial:
                raise forms.ValidationError(
                    "El valor de salvamento no puede ser igual al valor inicial; "
                    "no habría depreciación que calcular."
                )

        return data