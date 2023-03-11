from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VisualStructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.visual_structure"
    verbose_name = _("Visual Structure")
