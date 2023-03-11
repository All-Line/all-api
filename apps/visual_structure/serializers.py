from rest_framework import serializers

from apps.visual_structure.models import ColorModel, ColorPaletteModel


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorModel
        fields = ["title", "color"]


class ColorPaletteSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True)

    class Meta:
        model = ColorPaletteModel
        fields = ["id", "is_active", "title", "description", "colors"]
