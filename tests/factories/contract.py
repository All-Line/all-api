import factory

from apps.buying.models import ContractModel
from tests.factories.package import PackageFactory
from tests.factories.user import UserFactory


class ContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContractModel

    receipt = "some_receipt"
    user = factory.SubFactory(UserFactory)
    package = factory.SubFactory(PackageFactory)
