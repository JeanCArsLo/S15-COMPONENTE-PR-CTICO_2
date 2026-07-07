import json

from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskModelTests(TestCase):
    def test_str_devuelve_el_titulo(self):
        task = Task.objects.create(title="Configurar CI")
        self.assertEqual(str(task), "Configurar CI")

    def test_estado_por_defecto_es_pendiente(self):
        task = Task.objects.create(title="Nueva tarea")
        self.assertEqual(task.status, Task.Status.PENDING)

    def test_orden_por_posicion(self):
        Task.objects.create(title="Segunda", position=1)
        Task.objects.create(title="Primera", position=0)
        titles = list(Task.objects.values_list("title", flat=True))
        self.assertEqual(titles, ["Primera", "Segunda"])


class TaskBoardViewTests(TestCase):
    def test_tablero_responde_200(self):
        response = self.client.get(reverse("tasks:board"))
        self.assertEqual(response.status_code, 200)

    def test_tablero_tiene_una_columna_por_estado(self):
        response = self.client.get(reverse("tasks:board"))
        columns = response.context["columns"]
        self.assertEqual(len(columns), len(Task.Status.choices))

    def test_las_tareas_aparecen_en_su_columna(self):
        Task.objects.create(title="En curso", status=Task.Status.IN_PROGRESS)
        response = self.client.get(reverse("tasks:board"))
        columns = {c["key"]: c["tasks"] for c in response.context["columns"]}
        self.assertEqual(len(columns[Task.Status.IN_PROGRESS]), 1)
        self.assertEqual(len(columns[Task.Status.PENDING]), 0)


class TaskCreateViewTests(TestCase):
    def test_crea_tarea_y_redirige_al_tablero(self):
        response = self.client.post(
            reverse("tasks:create"),
            {"title": "Tarea nueva", "description": "", "status": Task.Status.PENDING},
        )
        self.assertRedirects(response, reverse("tasks:board"))
        self.assertEqual(Task.objects.count(), 1)

    def test_la_nueva_tarea_va_al_final_de_su_columna(self):
        Task.objects.create(title="Existente", position=3)
        self.client.post(
            reverse("tasks:create"),
            {"title": "Al final", "description": "", "status": Task.Status.PENDING},
        )
        task = Task.objects.get(title="Al final")
        self.assertEqual(task.position, 4)

    def test_titulo_vacio_no_crea_tarea(self):
        response = self.client.post(
            reverse("tasks:create"),
            {"title": "", "description": "", "status": Task.Status.PENDING},
        )
        self.assertEqual(response.status_code, 200)  # re-renderiza el form con errores
        self.assertEqual(Task.objects.count(), 0)


class TaskUpdateViewTests(TestCase):
    def test_actualiza_la_tarea(self):
        task = Task.objects.create(title="Original")
        response = self.client.post(
            reverse("tasks:update", args=[task.pk]),
            {"title": "Editada", "description": "", "status": Task.Status.COMPLETED},
        )
        self.assertRedirects(response, reverse("tasks:board"))
        task.refresh_from_db()
        self.assertEqual(task.title, "Editada")
        self.assertEqual(task.status, Task.Status.COMPLETED)

    def test_tarea_inexistente_da_404(self):
        response = self.client.get(reverse("tasks:update", args=[999]))
        self.assertEqual(response.status_code, 404)


class TaskDeleteViewTests(TestCase):
    def test_get_muestra_confirmacion_sin_borrar(self):
        task = Task.objects.create(title="A borrar")
        response = self.client.get(reverse("tasks:delete", args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 1)

    def test_post_elimina_la_tarea(self):
        task = Task.objects.create(title="A borrar")
        response = self.client.post(reverse("tasks:delete", args=[task.pk]))
        self.assertRedirects(response, reverse("tasks:board"))
        self.assertEqual(Task.objects.count(), 0)


class TaskReorderViewTests(TestCase):
    def _post_json(self, payload):
        return self.client.post(
            reverse("tasks:reorder"),
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_reordena_y_cambia_de_columna(self):
        t1 = Task.objects.create(title="Uno", status=Task.Status.PENDING, position=0)
        t2 = Task.objects.create(title="Dos", status=Task.Status.PENDING, position=1)
        response = self._post_json(
            {"columns": {"PENDING": [t2.pk], "IN_PROGRESS": [t1.pk]}}
        )
        self.assertEqual(response.status_code, 200)
        t1.refresh_from_db()
        t2.refresh_from_db()
        self.assertEqual(t1.status, Task.Status.IN_PROGRESS)
        self.assertEqual(t1.position, 0)
        self.assertEqual(t2.status, Task.Status.PENDING)
        self.assertEqual(t2.position, 0)

    def test_json_invalido_da_400(self):
        response = self.client.post(
            reverse("tasks:reorder"),
            data="esto no es json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_estado_desconocido_da_400(self):
        response = self._post_json({"columns": {"INVENTADO": []}})
        self.assertEqual(response.status_code, 400)

    def test_get_no_permitido(self):
        response = self.client.get(reverse("tasks:reorder"))
        self.assertEqual(response.status_code, 405)
