import factory

from apps.material.models import CourseCategoryModel
from tests.factories.color import ColorFactory


class CourseCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseCategoryModel

    title = "Some Title"
    description = "Some Description"
    color = factory.SubFactory(ColorFactory)
