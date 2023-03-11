import factory

from apps.material.models import CommentModel
from tests.factories.lesson import LessonFactory
from tests.factories.user import UserFactory


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentModel

    text = "Some Text"
    lesson = factory.SubFactory(LessonFactory)
    author = factory.SubFactory(UserFactory)
