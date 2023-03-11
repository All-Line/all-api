from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.material.models import LiveModel


@admin.register(LiveModel)
class LiveAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "slug",
        "is_paid",
        "starts_at",
        "live_type",
        "service",
        "is_active",
    ]
    search_fields = ["title", "slug", "starts_at", "live_type", "service"]
    list_filter = ["live_type", "service", "starts_at"]

    fieldsets = (
        (
            _("Identification"),
            {
                "fields": (
                    "service",
                    "title",
                    "description",
                    "image",
                    "slug",
                    "is_paid",
                )
            },
        ),
        (_("Settings"), {"fields": ("starts_at", "integration_field", "live_type")}),
    )
