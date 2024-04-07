from django.contrib import admin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from utils.admin import admin_method_attributes
from utils.admin.mixins import AttachmentPreviewMixin

from ..social.models import EventModel, ReactionTypeModel
from .models import (
    ServiceClientModel,
    ServiceCredentialConfigModel,
    ServiceEmailConfigModel,
    ServiceModel,
    SocialGraphModel,
)


class ServiceEmailConfigInline(admin.StackedInline):
    model = ServiceEmailConfigModel
    verbose_name_plural = "Service Email Configs"
    extra = 0

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email_sender",
                    "email_config_type",
                    "email_html_template",
                    "email_subject",
                    "email_link",
                    "email_link_expiration",
                )
            },
        ),
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


class ReactionTypeInline(AttachmentPreviewMixin, admin.TabularInline):
    model = ReactionTypeModel
    verbose_name_plural = "Reaction Types"
    extra = 0
    fields = (
        "name",
        "attachment",
        "clicked_image",
        "attachment_preview",
        "clicked_image_preview",
    )
    readonly_fields = ("attachment_preview", "clicked_image_preview")

    @staticmethod
    @admin_method_attributes(short_description=_("Clicked Image preview"))
    def clicked_image_preview(obj):
        if not obj.clicked_image:
            return _("No attachment")

        return mark_safe(f'<img src="{obj.clicked_image.url}" width="300px" />')


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
    inlines = [ServiceEmailConfigInline, ReactionTypeInline, EventInline]
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


@admin.register(ServiceClientModel)
class ServiceClientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug", "url", "is_active", "service"]
    readonly_fields = ["id", "date_joined", "date_modified"]
    list_filter = ["service", "is_active"]
    filter_horizontal = ["colors_palettes"]
    fieldsets = (
        (
            _("Identification"),
            {
                "fields": (
                    "id",
                    "service",
                    "name",
                    "slug",
                    "url",
                )
            },
        ),
        (
            _("Config"),
            {
                "fields": (
                    "is_active",
                    "date_joined",
                    "date_modified",
                    "colors_palettes",
                )
            },
        ),
    )


@admin.register(SocialGraphModel)
class SocialGraphModelAdmin(admin.ModelAdmin):
    list_display = [
        "service",
        "providers",
        "searcher",
        "graph_image_preview_basic",
        "generate_graph_image_button",
    ]
    readonly_fields = [
        "id",
        "date_joined",
        "date_modified",
        "graph_image_preview",
        "generate_graph_image_button_retrieved",
    ]
    list_filter = ["service", "provider", "searcher"]
    fieldsets = (
        (
            _("Service"),
            {"fields": ("service",)},
        ),
        (
            _("Config"),
            {
                "fields": (
                    "provider",
                    "searcher",
                    "color",
                )
            },
        ),
        (
            _("Social Graph"),
            {
                "fields": (
                    "graph_image_preview",
                    "generate_graph_image_button_retrieved",
                )
            },
        ),
    )
    filter_horizontal = ["provider"]
    actions = ["generate_graph_image"]

    def generate_graph_image(self, request, queryset):
        for social_graph in queryset:
            social_graph.generate_graph_image()

    generate_graph_image.short_description = _("Generate Social Graph Image")

    @staticmethod
    @admin_method_attributes(short_description=_("Graph Image"))
    def graph_image_preview(obj):
        if not obj.graph_image:
            return _("No attachment")

        return mark_safe(f'<img src="{obj.graph_image}" width="100%" />')

    @staticmethod
    @admin_method_attributes(short_description=_("Graph Image"))
    def graph_image_preview_basic(obj):
        if not obj.graph_image:
            return _("No attachment")

        return mark_safe(f'<img src="{obj.graph_image}" width="300px" />')

    @staticmethod
    @admin_method_attributes(short_description=_("Providers"))
    def providers(obj):
        return ", ".join([provider.name for provider in obj.provider.all()])

    @staticmethod
    @admin_method_attributes(short_description=_("Action"))
    def generate_graph_image_button(obj):
        return (
            "<a "
            'class="btn btn-high btn-success" '
            f'href="/admin/service/socialgraphmodel/{obj.id}/generate_graph_image/">'
            f'{_("Generate Graph Image")}'
            "</a>"
        )

    @staticmethod
    @admin_method_attributes(short_description=_("Action"))
    def generate_graph_image_button_retrieved(obj):
        return (
            "<a "
            'class="btn btn-high btn-success" '
            f'href="/admin/service/socialgraphmodel/{obj.id}'
            '/generate_graph_image_retrieved/">'
            f'{_("Generate Graph Image")}'
            "</a>"
        )

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:social_graph_id>/generate_graph_image/",
                self.admin_site.admin_view(self.generate_graph_image_view),
                name="generate_graph_image",
            ),
            path(
                "<int:social_graph_id>/generate_graph_image_retrieved/",
                self.admin_site.admin_view(self.generate_graph_image_view_retrieved),
                name="generate_graph_image_retrieved",
            ),
        ]
        return custom_urls + urls

    def generate_graph_image_view(self, request, social_graph_id):
        social_graph = SocialGraphModel.objects.get(id=social_graph_id)
        social_graph.generate_graph_image()
        return self.response_change(request, social_graph)

    def generate_graph_image_view_retrieved(self, request, social_graph_id):
        social_graph = SocialGraphModel.objects.get(id=social_graph_id)
        social_graph.generate_graph_image()

        # Precisa continuar na página de edição para exibir a imagem
        return redirect(f"/admin/service/socialgraphmodel/{social_graph_id}/change/")
