import factory
from django.contrib.auth.hashers import make_password

from apps.user.models import UserModel
from tests.factories.service import ServiceFactory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserModel

    email = "some@email.com"
    password = factory.LazyFunction(lambda: make_password("12345Aa@"))
    first_name = "some first_name"
    last_name = "some last_name"
    service = factory.SubFactory(ServiceFactory)
