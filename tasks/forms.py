from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "input", "placeholder": "Ej: Configurar pipeline CI/CD"}
            ),
            "description": forms.Textarea(
                attrs={"class": "input", "rows": 4, "placeholder": "Detalles de la tarea..."}
            ),
            "status": forms.Select(attrs={"class": "input"}),
        }
