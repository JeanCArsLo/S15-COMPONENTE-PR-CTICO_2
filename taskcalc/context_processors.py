"""Context processors del proyecto: exponen los feature flags a los templates."""
from django.conf import settings


def feature_flags(request):
    """Permite usar {{ FEATURE_CALCULATOR }} en cualquier template."""
    return {
        "FEATURE_CALCULATOR": settings.FEATURE_CALCULATOR,
    }
