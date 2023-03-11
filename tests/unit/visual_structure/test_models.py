from colorfield.fields import ColorField
from django.db import models

from apps.visual_structure.models import ColorModel, ColorPaletteModel
from utils.abstract_models.base_model import BaseModel


class TestColorModel:
    @classmethod
    def setup_class(cls):
        cls.model = ColorModel

    def test_str(self):
        color = ColorModel(title="foo")

        assert str(color) == "foo (#FFFFFF)"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Color"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Colors"

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255

    def test_color_field(self):
        field = self.model._meta.get_field("color")

        assert type(field) == ColorField
        assert field.verbose_name == "Color"
        assert field.default == "#FFFFFF"
        assert field.format == "hexa"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 6


class TestColorPaletteModel:
    @classmethod
    def setup_class(cls):
        cls.model = ColorPaletteModel

    def test_str(self):
        color_palette = ColorPaletteModel(title="foo")

        assert str(color_palette) == "foo"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Color Palette"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Color Palettes"

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255

    def test_description_field(self):
        field = self.model._meta.get_field("description")

        assert type(field) == models.TextField
        assert field.verbose_name == "Description"
        assert field.null is True
        assert field.blank is True

    def test_colors_field(self):
        field = self.model._meta.get_field("colors")

        assert type(field) == models.ManyToManyField
        assert field.verbose_name == "Colors"
        assert field.remote_field.related_name == "color_palettes"
        assert field.related_model == ColorModel

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 6
