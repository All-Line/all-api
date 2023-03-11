import factory

from apps.buying.models import PackageModel
from tests.factories.service import ServiceFactory
from tests.factories.store import StoreFactory


class PackageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackageModel

    label = "Some Label"
    price = 100
    slug = factory.Faker("slug")
    store = factory.SubFactory(StoreFactory)
    service = factory.SubFactory(ServiceFactory)
