import factory

from apps.material.models import LessonModel
from tests.factories.course import CourseFactory


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LessonModel

    title = "Some Title"
    description = "Some Description"
    course = factory.SubFactory(CourseFactory)
    lesson_type = "text"
    text = "Some Text"
    reading_time = 1
