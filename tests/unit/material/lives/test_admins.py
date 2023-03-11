from django.contrib import admin
from django.contrib.admin import AdminSite

from apps.material.admin import LiveAdmin
from apps.material.models import LiveModel


class TestLiveAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = LiveAdmin(LiveModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == LiveModel

    def test_admin_subclass(self):
        assert issubclass(LiveAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "title",
            "slug",
            "is_paid",
            "starts_at",
            "live_type",
            "service",
            "is_active",
        ]

    def test_search_fields(self):
        assert self.admin.search_fields == [
            "title",
            "slug",
            "starts_at",
            "live_type",
            "service",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == ["live_type", "service", "starts_at"]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
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
        )

    def test_fieldsets_settings(self):
        assert self.admin.fieldsets[1] == (
            "Settings",
            {"fields": ("starts_at", "integration_field", "live_type")},
        )
