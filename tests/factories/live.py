import factory
from django.utils import timezone

from apps.material.models import LiveModel
from tests.factories.service import ServiceFactory


class LiveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LiveModel

    title = "Some Title"
    description = "Some Description"
    slug = "some_slug"
    is_paid = True
    service = factory.SubFactory(ServiceFactory)
    starts_at = timezone.now()
    integration_field = "some_integration"
    live_type = "live_class"
