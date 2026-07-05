import json

from django.contrib import messages
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TaskForm
from .models import Task


def task_board(request):
    """Tablero Kanban: una columna por estado, ordenado por prioridad."""
    tasks = Task.objects.all()
    columns = [
        {
            "key": value,
            "label": label,
            "tasks": [t for t in tasks if t.status == value],
        }
        for value, label in Task.Status.choices
    ]
    return render(request, "tasks/task_board.html", {"columns": columns})


def task_create(request):
    """Crea una tarea y la coloca al final de su columna."""
    form = TaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        last = Task.objects.filter(status=task.status).aggregate(m=Max("position"))["m"]
        task.position = 0 if last is None else last + 1
        task.save()
        messages.success(request, "Tarea creada correctamente.")
        return redirect("tasks:board")
    return render(request, "tasks/task_form.html", {"form": form, "title": "Nueva tarea"})


def task_update(request, pk):
    """Edita una tarea existente."""
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tarea actualizada correctamente.")
        return redirect("tasks:board")
    return render(request, "tasks/task_form.html", {"form": form, "title": "Editar tarea"})


def task_delete(request, pk):
    """Elimina una tarea (con confirmación)."""
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Tarea eliminada.")
        return redirect("tasks:board")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@require_POST
def task_reorder(request):
    """
    Guarda el resultado del drag & drop.

    Recibe JSON: {"columns": {"PENDING": [ids...], "IN_PROGRESS": [...], ...}}
    La posición en la lista define la prioridad (0 = más importante).
    """
    try:
        data = json.loads(request.body)
        columns = data["columns"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "JSON inválido"}, status=400)

    valid_statuses = {value for value, _ in Task.Status.choices}
    if not set(columns).issubset(valid_statuses):
        return JsonResponse({"error": "Estado desconocido"}, status=400)

    for status, ids in columns.items():
        for position, task_id in enumerate(ids):
            Task.objects.filter(pk=task_id).update(status=status, position=position)

    return JsonResponse({"ok": True})
