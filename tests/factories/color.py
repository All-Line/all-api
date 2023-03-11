import factory

from apps.visual_structure.models import ColorModel


class ColorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ColorModel

    title = "Some Title"
    color = "#FFFFFF"
