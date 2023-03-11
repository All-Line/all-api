from colorfield.fields import ColorField
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.abstract_models.base_model import BaseModel


class ColorModel(BaseModel):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    color = ColorField(verbose_name=_("Color"), default="#FFFFFF", format="hexa")

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")

    def __str__(self):
        return f"{self.title} ({self.color})"


class ColorPaletteModel(BaseModel):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    colors = models.ManyToManyField(
        ColorModel, related_name="color_palettes", verbose_name=_("Colors")
    )

    class Meta:
        verbose_name = _("Color Palette")
        verbose_name_plural = _("Color Palettes")

    def __str__(self):
        return self.title
