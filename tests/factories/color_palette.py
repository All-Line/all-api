import factory

from apps.visual_structure.models import ColorPaletteModel


class ColorPaletteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ColorPaletteModel

    title = "Some Title"
    description = "Some Description"
