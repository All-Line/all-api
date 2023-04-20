from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.admin import admin_method_attributes

from ..social.models import EventModel, ReactionTypeModel
from .models import (
    ServiceCredentialConfigModel,
    ServiceEmailConfigModel,
    ServiceModel,
)


class ServiceEmailConfigInline(admin.TabularInline):
    model = ServiceEmailConfigModel
    verbose_name_plural = "Service Email Configs"
    extra = 0
    fields = (
        "email_config_type",
        "email_html_template",
        "email_subject",
        "email_link",
        "email_link_expiration",
    )


class ServiceCredentialLoginConfigInline(admin.TabularInline):
    model = ServiceCredentialConfigModel
    verbose_name_plural = "Service Login Fields Config"
    extra = 0
    fields = (
        "credential_config_type",
        "field",
        "label",
        "field_html_type",
        "rule",
        "no_match_message",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(credential_config_type="login")


class ServiceCredentialRegisterConfigInline(admin.TabularInline):
    model = ServiceCredentialConfigModel
    verbose_name_plural = "Service Register Fields Config"
    extra = 0
    fields = (
        "credential_config_type",
        "field",
        "label",
        "field_html_type",
        "rule",
        "no_match_message",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(credential_config_type="register")


class ReactionTypeInline(admin.TabularInline):
    model = ReactionTypeModel
    verbose_name_plural = "Reaction Types"
    extra = 0
    fields = (
        "name",
        "attachment",
    )


class EventInline(admin.TabularInline):
    model = EventModel
    verbose_name_plural = "Events"
    extra = 0
    fields = (
        "title",
        "description",
        "attachment",
        "event_type",
        "guests",
    )


@admin.register(ServiceModel)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [ReactionTypeInline, EventInline]
    list_display = [
        "name",
        "slug",
        "custom_url",
        "language",
        "is_active",
    ]
    list_filter = ["language", "is_active", "date_joined", "date_modified"]
    readonly_fields = ["id"]
    filter_horizontal = ["colors_palettes"]
    fieldsets = (
        (
            _("Identification"),
            {
                "fields": (
                    "id",
                    "name",
                    "slug",
                    "language",
                    "url",
                    "terms",
                )
            },
        ),
        (
            _("SMTP Configuration"),
            {"fields": ("smtp_email",)},
        ),
        (
            _("Interaction"),
            {"fields": ("confirmation_required",)},
        ),
        ("Settings", {"fields": ("colors_palettes",)}),
    )

    def save_model(self, request, obj, form, change):
        if change:
            obj.date_modified = timezone.now()

        obj.save()

    @staticmethod
    @admin_method_attributes(short_description=_("Page"))
    def custom_url(service):
        return (
            "<a "
            'class="btn btn-high btn-success" '
            'target="_blank" '
            f'href="{service.url}">'
            f'{_("Access the service page")}'
            "</a>"
        )
