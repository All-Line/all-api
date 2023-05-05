from unittest.mock import Mock, patch

from django.contrib import admin
from django.contrib.admin import AdminSite

from apps.service.admin import (
    EventInline,
    ReactionTypeInline,
    ServiceAdmin,
    ServiceCredentialLoginConfigInline,
    ServiceCredentialRegisterConfigInline,
    ServiceEmailConfigInline,
)
from apps.service.models import (
    ServiceCredentialConfigModel,
    ServiceEmailConfigModel,
    ServiceModel,
)
from apps.social.models import EventModel, ReactionTypeModel


class TestServiceAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = ServiceAdmin(ServiceModel, AdminSite())

    def test_parent_class(self):
        assert issubclass(ServiceAdmin, admin.ModelAdmin)

    def test_inlines(self):
        assert self.admin.inlines == [
            ReactionTypeInline,
            EventInline,
        ]

    def test_list_display(self):
        assert self.admin.list_display == [
            "name",
            "slug",
            "custom_url",
            "language",
            "is_active",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "language",
            "is_active",
            "date_joined",
            "date_modified",
        ]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id"]

    def test_filter_horizontal(self):
        assert self.admin.filter_horizontal == ["colors_palettes"]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
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
        )

    def test_fieldsets_smtp_configuration(self):
        assert self.admin.fieldsets[1] == (
            "SMTP Configuration",
            {"fields": ("smtp_email",)},
        )

    def test_fieldsets_smtp_interaction(self):
        assert self.admin.fieldsets[2] == (
            "Interaction",
            {"fields": ("confirmation_required",)},
        )

    def test_fieldsets_settings(self):
        assert self.admin.fieldsets[3] == (
            "Settings",
            {"fields": ("colors_palettes",)},
        )

    @patch("apps.service.admin.timezone")
    def test_save_model_with_change(self, mock_timezone):
        mock_obj = Mock()
        self.admin.save_model(None, mock_obj, None, True)

        mock_timezone.now.assert_called_once()
        assert mock_obj.date_modified == mock_timezone.now.return_value
        mock_obj.save.assert_called_once()

    @patch("apps.service.admin.timezone")
    def test_save_model_without_change(self, mock_timezone):
        mock_obj = Mock()
        self.admin.save_model(None, mock_obj, None, False)

        mock_timezone.now.assert_not_called()
        mock_obj.save.assert_called_once()

    def test_custom_url(self):
        service = Mock()
        result = self.admin.custom_url(service)

        assert result == (
            "<a "
            'class="btn btn-high btn-success" '
            'target="_blank" '
            f'href="{service.url}">'
            "Access the service page"
            "</a>"
        )


class TestServiceEmailConfigInline:
    @classmethod
    def setup_class(cls):
        cls.inline = ServiceEmailConfigInline(Mock(), AdminSite())

    def test_parent_class(self):
        assert issubclass(ServiceEmailConfigInline, admin.TabularInline)

    def test_model(self):
        assert self.inline.model == ServiceEmailConfigModel

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Service Email Configs"

    def test_extra(self):
        assert self.inline.extra == 0

    def test_fields(self):
        assert self.inline.fields == (
            "email_config_type",
            "email_html_template",
            "email_subject",
            "email_link",
            "email_link_expiration",
        )


class TestServiceCredentialLoginConfigInline:
    @classmethod
    def setup_class(cls):
        cls.inline = ServiceCredentialLoginConfigInline(Mock(), AdminSite())

    def test_parent_class(self):
        assert issubclass(ServiceCredentialLoginConfigInline, admin.TabularInline)

    def test_model(self):
        assert self.inline.model == ServiceCredentialConfigModel

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Service Login Fields Config"

    def test_extra(self):
        assert self.inline.extra == 0

    def test_fields(self):
        assert self.inline.fields == (
            "credential_config_type",
            "field",
            "label",
            "field_html_type",
            "rule",
            "no_match_message",
        )

    @patch("apps.service.admin.super")
    def test_get_queryset(self, mock_super):
        queryset = mock_super.return_value.get_queryset.return_value
        result = self.inline.get_queryset({})

        mock_super.assert_called_once()
        mock_super.return_value.get_queryset.assert_called_once_with({})
        queryset.filter.assert_called_once_with(credential_config_type="login")
        assert result == queryset.filter.return_value


class TestServiceCredentialRegisterConfigInline:
    @classmethod
    def setup_class(cls):
        cls.inline = ServiceCredentialRegisterConfigInline(Mock(), AdminSite())

    def test_parent_class(self):
        assert issubclass(ServiceCredentialRegisterConfigInline, admin.TabularInline)

    def test_model(self):
        assert self.inline.model == ServiceCredentialConfigModel

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Service Register Fields Config"

    def test_extra(self):
        assert self.inline.extra == 0

    def test_fields(self):
        assert self.inline.fields == (
            "credential_config_type",
            "field",
            "label",
            "field_html_type",
            "rule",
            "no_match_message",
        )

    @patch("apps.service.admin.super")
    def test_get_queryset(self, mock_super):
        queryset = mock_super.return_value.get_queryset.return_value
        result = self.inline.get_queryset({})

        mock_super.assert_called_once()
        mock_super.return_value.get_queryset.assert_called_once_with({})
        queryset.filter.assert_called_once_with(credential_config_type="register")
        assert result == queryset.filter.return_value


class TestReactionTypeInline:
    def test_parent_class(self):
        assert issubclass(ReactionTypeInline, admin.TabularInline)

    def test_model(self):
        assert ReactionTypeInline.model == ReactionTypeModel

    def test_verbose_name_plural(self):
        assert ReactionTypeInline.verbose_name_plural == "Reaction Types"

    def test_extra(self):
        assert ReactionTypeInline.extra == 0

    def test_fields(self):
        assert ReactionTypeInline.fields == (
            "name",
            "attachment",
        )


class TestEventInline:
    def test_parent_class(self):
        assert issubclass(EventInline, admin.TabularInline)

    def test_model(self):
        assert EventInline.model == EventModel

    def test_extra(self):
        assert EventInline.extra == 0

    def test_verbose_name_plural(self):
        assert EventInline.verbose_name_plural == "Events"

    def test_fields(self):
        assert EventInline.fields == (
            "title",
            "description",
            "attachment",
            "event_type",
            "guests",
        )
