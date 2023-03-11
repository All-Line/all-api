from rest_framework import serializers

from apps.service.models import ServiceCredentialConfigModel, ServiceModel
from apps.service.serializers import (
    RetrieveServiceSerializer,
    ServiceCredentialConfigSerializer,
)


class TestRetrieveServiceSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = RetrieveServiceSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == ServiceModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "is_active",
            "name",
            "slug",
            "url",
            "colors_palettes",
            "confirmation_required",
            "language",
            "terms",
        ]

    def test_meta_depth(self):
        assert self.serializer.Meta.depth == 1


class TestServiceCredentialConfigSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = ServiceCredentialConfigSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == ServiceCredentialConfigModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "credential_config_type",
            "field",
            "label",
            "field_html_type",
            "rule",
            "no_match_message",
        ]
