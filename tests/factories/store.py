import factory

from apps.buying.models import StoreModel


class StoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StoreModel

    name = "Some Name"
    backend = "dummy"
