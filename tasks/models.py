from django.db import models


class Task(models.Model):
    """Tarea del tablero: título, descripción, estado y posición (prioridad)."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        IN_PROGRESS = "IN_PROGRESS", "En curso"
        COMPLETED = "COMPLETED", "Finalizada"

    title = models.CharField("Título", max_length=120)
    description = models.TextField("Descripción", blank=True)
    status = models.CharField(
        "Estado",
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    # Orden dentro de la columna: 0 = mayor importancia
    position = models.PositiveIntegerField("Posición", default=0)
    created_at = models.DateTimeField("Creada", auto_now_add=True)

    class Meta:
        ordering = ["position", "created_at"]
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"

    def __str__(self):
        return self.title
