from rest_framework import serializers

from apps.service.models import ServiceCredentialConfigModel, ServiceModel
from apps.visual_structure.serializers import ColorPaletteSerializer


class RetrieveServiceSerializer(serializers.ModelSerializer):
    colors_palettes = ColorPaletteSerializer(many=True)

    class Meta:
        model = ServiceModel
        fields = [
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
        depth = 1


class TermsServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceModel
        fields = ["terms"]


class ServiceCredentialConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCredentialConfigModel
        fields = [
            "id",
            "credential_config_type",
            "field",
            "label",
            "field_html_type",
            "rule",
            "no_match_message",
        ]
