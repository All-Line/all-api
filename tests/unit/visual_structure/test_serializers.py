from rest_framework import serializers

from apps.visual_structure.models import ColorModel, ColorPaletteModel
from apps.visual_structure.serializers import (
    ColorPaletteSerializer,
    ColorSerializer,
)


class TestColorSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = ColorSerializer

    def test_subclass_serializer(self):
        assert issubclass(ColorSerializer, serializers.ModelSerializer)

    def test_model(self):
        assert self.serializer.Meta.model == ColorModel

    def test_fields(self):
        assert self.serializer.Meta.fields == ["title", "color"]


class TestColorPaletteSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = ColorPaletteSerializer

    def test_subclass_serializer(self):
        assert issubclass(ColorPaletteSerializer, serializers.ModelSerializer)

    def test_model(self):
        assert self.serializer.Meta.model == ColorPaletteModel

    def test_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "is_active",
            "title",
            "description",
            "colors",
        ]
