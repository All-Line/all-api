from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.visual_structure.models import ColorModel, ColorPaletteModel
from utils.admin import admin_method_attributes


@admin.register(ColorModel)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["id", "title_with_color_preview", "color"]
    list_filter = ["color"]
    search_fields = ["title"]
    readonly_fields = ["id"]
    fieldsets = ((_("Identification"), {"fields": ("title", "color")}),)

    @staticmethod
    @admin_method_attributes(short_description=_("Title"))
    def title_with_color_preview(color):
        style = (
            f"background-color: {color.color}; width: 20px; "
            "height: 20px; border: 2px solid gray; "
            "margin-right: 5px; border-radius: 5px"
        )

        return (
            "<div style='display:flex; align-items: center'>"
            f"<div style='{style}'></div>"
            f"<div>{color.title}</div>"
            "</div>"
        )


@admin.register(ColorPaletteModel)
class ColorPaletteAdmin(admin.ModelAdmin):
    list_display = ["id", "colors_preview", "title", "description"]
    search_fields = ["title"]
    filter_horizontal = ["colors"]
    readonly_fields = ["id"]
    fieldsets = (
        (_("Identification"), {"fields": ("title", "colors", "description")}),
    )

    @admin_method_attributes(short_description=_("Colors preview"))
    def colors_preview(self, color_palette):
        result = "".join(
            [
                f"<div style='background-color: {color.color}; "
                "width: 20px; height: 20px; border: 2px solid gray; "
                "margin-right: 5px; border-radius: 5px'></div>"
                for color in color_palette.colors.iterator()
            ]
        )

        return f"<div style='display:flex; align-items: center'>{result}</div>"
