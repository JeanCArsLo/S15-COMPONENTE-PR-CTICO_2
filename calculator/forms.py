from django import forms


class DepreciationForm(forms.Form):
    """Datos para el cálculo de depreciación por Línea Recta."""

    initial_value = forms.DecimalField(
        label="Valor Inicial (S/.)",
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "input", "placeholder": "Ej: 10000", "step": "0.01"}
        ),
    )
    useful_life = forms.IntegerField(
        label="Vida Útil (años)",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": "Ej: 5"}),
    )
    salvage_value = forms.DecimalField(
        label="Valor de Salvamento (S/.)",
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "input", "placeholder": "Ej: 1000", "step": "0.01"}
        ),
    )

    def clean(self):
        data = super().clean()
        initial = data.get("initial_value")
        salvage = data.get("salvage_value")
        if initial is not None and salvage is not None and salvage > initial:
            raise forms.ValidationError(
                "El valor de salvamento no puede ser mayor que el valor inicial."
            )
        return data
