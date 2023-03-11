from rest_framework import serializers

from apps.material.models import LiveModel


class LiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveModel
        fields = [
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
