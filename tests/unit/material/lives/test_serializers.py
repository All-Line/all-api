from rest_framework import serializers

from apps.material.models import LiveModel
from apps.material.serializers import LiveSerializer


class TestLiveSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = LiveSerializer

    def test_subclass_serializer(self):
        assert issubclass(LiveSerializer, serializers.ModelSerializer)

    def test_model(self):
        assert self.serializer.Meta.model == LiveModel

    def test_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "title",
            "description",
            "slug",
            "is_paid",
            "starts_at",
            "integration_field",
            "live_type",
            "image",
        ]
