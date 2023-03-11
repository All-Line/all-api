import factory

from apps.service.models import ServiceCredentialConfigModel
from tests.factories.service import ServiceFactory


class ServiceCredentialConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceCredentialConfigModel

    service = factory.SubFactory(ServiceFactory)
    credential_config_type = "login"
    field = "foo"
    label = "Some Label"
    field_html_type = "Some html type"
    rule = "Some rule"
    no_match_message = "Some no match message"
