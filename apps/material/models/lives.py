from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.service.models import ServiceModel
from utils.abstract_models.base_model import BaseModel

from .utils.file import material_file_directory_path


class LiveModel(BaseModel):
    LIVE_TYPE_CHOICES = (
        ("live_class", "Live Class"),
        ("interactive_class", "Interactive Class"),
    )

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))
    slug = models.SlugField(verbose_name=_("Slug"))
    is_paid = models.BooleanField(verbose_name=_("Is Paid"), default=True)
    starts_at = models.DateTimeField(
        verbose_name=_("Starts At"), help_text=_("The day and time the live will start")
    )
    integration_field = models.TextField(
        verbose_name=_("Integration Field"),
        help_text=_(
            "This field controls the integration that will be made for the Live to "
            "happen. Fields like Youtube ID, Vimeo ID, Zoom JSON, etc are accepted."
        ),
    )
    live_type = models.CharField(
        verbose_name=_("Type"),
        max_length=255,
        choices=LIVE_TYPE_CHOICES,
        default="live_class",
    )
    image = models.FileField(
        verbose_name=_("Image"),
        upload_to=material_file_directory_path,
        null=True,
        blank=True,
    )

    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="lives",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Live")
        verbose_name_plural = _("Lives")

    def __str__(self):
        return self.title
