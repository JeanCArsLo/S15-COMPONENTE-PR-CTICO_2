from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import DepreciationForm


@override_settings(FEATURE_CALCULATOR=False)
class FeatureFlagOffTests(TestCase):
    def test_calculadora_desactivada_da_404(self):
        response = self.client.get(reverse("calculator:depreciation"))
        self.assertEqual(response.status_code, 404)


@override_settings(FEATURE_CALCULATOR=True)
class DepreciationViewTests(TestCase):
    def test_calculadora_activada_responde_200(self):
        response = self.client.get(reverse("calculator:depreciation"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["result"])

    def test_calculo_linea_recta(self):
        # (10000 - 1000) / 5 = 1800 anual
        response = self.client.post(
            reverse("calculator:depreciation"),
            {"initial_value": "10000", "useful_life": "5", "salvage_value": "1000"},
        )
        result = response.context["result"]
        self.assertEqual(result["annual"], Decimal("1800.00"))
        self.assertEqual(result["depreciable_base"], Decimal("9000.00"))
        self.assertEqual(len(result["schedule"]), 5)
        # Al final de la vida útil, el valor en libros es el valor de salvamento
        self.assertEqual(result["schedule"][-1]["book_value"], Decimal("1000.00"))
        self.assertEqual(result["schedule"][-1]["accumulated"], Decimal("9000.00"))

    def test_formulario_invalido_no_calcula(self):
        response = self.client.post(
            reverse("calculator:depreciation"),
            {"initial_value": "", "useful_life": "", "salvage_value": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["result"])


class DepreciationFormTests(TestCase):
    def test_salvamento_mayor_que_inicial_es_invalido(self):
        form = DepreciationForm(
            {"initial_value": "1000", "useful_life": "5", "salvage_value": "2000"}
        )
        self.assertFalse(form.is_valid())

    def test_vida_util_cero_es_invalida(self):
        form = DepreciationForm(
            {"initial_value": "1000", "useful_life": "0", "salvage_value": "100"}
        )
        self.assertFalse(form.is_valid())

    def test_datos_correctos_son_validos(self):
        form = DepreciationForm(
            {"initial_value": "10000", "useful_life": "5", "salvage_value": "1000"}
        )
        self.assertTrue(form.is_valid())
