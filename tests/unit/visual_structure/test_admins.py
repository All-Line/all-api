from unittest.mock import Mock

from django.contrib import admin
from django.contrib.admin import AdminSite

from apps.visual_structure.admin import ColorAdmin, ColorPaletteAdmin
from apps.visual_structure.models import ColorModel, ColorPaletteModel


class TestColorAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = ColorAdmin(ColorModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == ColorModel

    def test_admin_subclass(self):
        assert issubclass(ColorAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "title_with_color_preview",
            "color",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == ["color"]

    def test_search_fields(self):
        assert self.admin.search_fields == ["title"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id"]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
            {"fields": ("title", "color")},
        )

    def test_title_with_color_preview(self):
        mock_color = Mock()
        result = self.admin.title_with_color_preview(mock_color)

        assert result == (
            "<div style='display:flex; align-items: center'>"
            f"<div style='background-color: {mock_color.color}; "
            "width: 20px; height: 20px; border: 2px solid gray; "
            "margin-right: 5px; border-radius: 5px'>"
            "</div>"
            f"<div>{mock_color.title}</div>"
            "</div>"
        )


class TestColorPaletteAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = ColorPaletteAdmin(ColorPaletteModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == ColorPaletteModel

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "colors_preview",
            "title",
            "description",
        ]

    def test_search_fields(self):
        assert self.admin.search_fields == ["title"]

    def test_filter_horizontal(self):
        assert self.admin.filter_horizontal == ["colors"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id"]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            ("Identification", {"fields": ("title", "colors", "description")})
        )

    def test_color_preview(self):
        mock_color_palette = Mock()
        mock_color_white = Mock(color="#FFFFFF")
        mock_color_black = Mock(color="#000000")
        mock_color_palette.colors.iterator.return_value = [
            mock_color_white,
            mock_color_black,
        ]

        result = self.admin.colors_preview(mock_color_palette)

        mock_color_palette.colors.iterator.assert_called_once()

        assert result == (
            f"<div style='display:flex; align-items: center'>"
            f"<div style='background-color: {mock_color_white.color}; "
            "width: 20px; height: 20px; border: 2px solid gray; "
            "margin-right: 5px; border-radius: 5px'></div>"
            f"<div style='background-color: {mock_color_black.color}; "
            "width: 20px; height: 20px; border: 2px solid gray; "
            "margin-right: 5px; border-radius: 5px'></div>"
            "</div>"
        )
