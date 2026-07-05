from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_board, name="board"),
    path("tareas/nueva/", views.task_create, name="create"),
    path("tareas/<int:pk>/editar/", views.task_update, name="update"),
    path("tareas/<int:pk>/eliminar/", views.task_delete, name="delete"),
    path("tareas/reordenar/", views.task_reorder, name="reorder"),
]
