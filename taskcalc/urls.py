"""Rutas principales del proyecto Task & Calc."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tasks.urls")),
    path("calculadora/", include("calculator.urls")),
]
