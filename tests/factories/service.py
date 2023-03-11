import factory

from apps.service.models import ServiceModel


class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceModel

    name = "Some Name"
    slug = factory.Faker("slug")
    url = "https://some_url.com"
    smtp_email = "smtp_email@test.com"
    language = "pt"
    terms = "Some Terms"
