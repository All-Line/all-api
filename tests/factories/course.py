import factory

from apps.material.models import CourseModel
from tests.factories.service import ServiceFactory


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseModel

    title = "Some Title"
    description = "Some Description"
    slug = "some_slug"
    is_paid = True
    service = factory.SubFactory(ServiceFactory)
    course_mode = "open"
