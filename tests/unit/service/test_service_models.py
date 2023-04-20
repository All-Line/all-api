from unittest.mock import Mock, call, patch

import pytest
from django.db import models
from rest_framework.exceptions import ValidationError

from apps.service.models import (
    ServiceCredentialConfigModel,
    ServiceEmailConfigModel,
    ServiceModel,
)
from apps.visual_structure.models import ColorPaletteModel
from utils.abstract_models.base_model import BaseModel
from utils.choices.language_choices import LANGUAGE_CHOICES


class TestServiceModel:
    @classmethod
    def setup_class(cls):
        cls.model = ServiceModel

    def test_str(self):
        service = ServiceModel(slug="foo")

        assert str(service) == "foo"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Service"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Services"

    def test_name_field(self):
        field = self.model._meta.get_field("name")

        assert type(field) == models.CharField
        assert field.verbose_name == "Name"

    def test_slug_field(self):
        field = self.model._meta.get_field("slug")

        assert type(field) == models.SlugField
        assert field.verbose_name == "Slug Field"

    def test_url_field(self):
        field = self.model._meta.get_field("url")

        assert type(field) == models.URLField
        assert field.verbose_name == "URL"
        assert field.null is True
        assert field.blank is True

    def test_smtp_email_field(self):
        field = self.model._meta.get_field("smtp_email")

        assert type(field) == models.EmailField
        assert field.verbose_name == "SMTP Email"
        assert field.null is True
        assert field.blank is True

    def test_colors_palettes_field(self):
        field = self.model._meta.get_field("colors_palettes")

        assert type(field) == models.ManyToManyField
        assert field.related_model == ColorPaletteModel
        assert field.remote_field.related_name == "services"
        assert field.verbose_name == "Colors Palettes"
        assert field.blank is True

    def test_confirmation_required_field(self):
        field = self.model._meta.get_field("confirmation_required")

        assert type(field) == models.BooleanField
        assert field.verbose_name == "Confirmation Required"
        assert field.default is True
        assert field.help_text == (
            "If it's true, users need to confirm "
            "their e-mails to use the application."
        )

    def test_language_field(self):
        field = self.model._meta.get_field("language")

        assert type(field) == models.CharField
        assert field.verbose_name == "Language"
        assert field.choices == LANGUAGE_CHOICES

    def test_terms_field(self):
        field = self.model._meta.get_field("terms")

        assert type(field) == models.TextField
        assert field.verbose_name == "Terms and Conditions"
        assert field.null is True
        assert field.blank is True

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 11

    def test_validate_credential_fields_failure_without_value(self):
        mock_field = Mock(
            field="foo",
            rule="[a-z]{8,}",
            no_match_message="The field does not have a valid format",
        )
        mock_config_type = Mock()
        mock_self = Mock()
        filtered_configs = (
            mock_self.credential_configs.only.return_value.filter
        )
        filtered_configs.return_value.iterator.return_value = [mock_field]
        request_data = {"bar": "foo"}

        with pytest.raises(ValidationError) as err:
            self.model.validate_credential_fields(
                mock_self, request_data, mock_config_type
            )

        filtered_config = filtered_configs.return_value

        mock_self.credential_configs.only.assert_called_once_with(
            "field", "rule", "no_match_message"
        )
        mock_self.credential_configs.only.return_value.filter.assert_called_once_with(
            credential_config_type=mock_config_type
        )
        filtered_config.iterator.assert_called_once()
        assert err.value.detail == {"foo": ["This field is required."]}

    def test_validate_credential_fields_with_field_does_not_match_rule(self):
        mock_field = Mock(
            field="foo",
            rule="[a-z]{8,}",
            no_match_message="The field does not have a valid format",
        )
        mock_config_type = Mock()
        mock_self = Mock()
        filtered_configs = (
            mock_self.credential_configs.only.return_value.filter
        )
        filtered_configs.return_value.iterator.return_value = [mock_field]
        request_data = {"foo": "bar"}

        with pytest.raises(ValidationError) as err:
            self.model.validate_credential_fields(
                mock_self, request_data, mock_config_type
            )

        filtered_config = (
            mock_self.credential_configs.only.return_value.filter.return_value
        )

        mock_self.credential_configs.only.assert_called_once_with(
            "field", "rule", "no_match_message"
        )
        mock_self.credential_configs.only.return_value.filter.assert_called_once_with(
            credential_config_type=mock_config_type
        )
        filtered_config.iterator.assert_called_once()
        assert err.value.detail == {
            "foo": "The field does not have a valid format"
        }

    def test_has_credential_configs(self):
        mock_self = Mock()
        mock_self.credential_configs.count.return_value = 1
        result = self.model.has_credential_configs(mock_self)

        assert result is True

    def test_clean(self):
        mock_configs = Mock()
        mock_configs.filter.return_value.count.return_value = 0
        mock_configs.count.return_value = 2
        mock_self = Mock()
        mock_self.has_credential_configs.return_value = True
        mock_self.credential_configs.filter.return_value = mock_configs

        with pytest.raises(ValidationError):
            self.model.clean(mock_self)

        mock_self.has_credential_configs.assert_called_once()
        assert mock_self.credential_configs.filter.call_args_list == [
            call(credential_config_type="login"),
            call(credential_config_type="register"),
        ]
        assert mock_configs.filter.call_args_list == [
            call(field="password"),
            call(field="password"),
        ]
        assert mock_configs.filter.return_value.count.call_args_list == [
            call(),
            call(),
        ]
        assert mock_configs.count.call_args_list == [call(), call()]

    @patch("apps.service.models.settings")
    @patch("apps.service.models.ServiceCredentialConfigModel")
    @patch("apps.service.models.super")
    def test_save(
        self, mock_super, mock_service_credential_config, mock_settings
    ):
        mock_settings.DEFAULT_CREDENTIAL_CONFIGS = [
            {
                "credential_config_type": "register",
                "field": "email",
                "label": "Write your email",
                "field_html_type": "email",
                "rule": r"^[a-z]{12,}",
                "no_match_message": "Invalid email",
            }
        ]
        mock_self = Mock()
        mock_self.has_credential_configs.return_value = False
        self.model.save(mock_self)

        mock_super.return_value.save.assert_called_once_with(
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
        )
        assert (
            mock_service_credential_config.objects.create.call_args_list
            == [
                call(
                    service=mock_self,
                    credential_config_type="register",
                    field="email",
                    label="Write your email",
                    field_html_type="email",
                    rule=r"^[a-z]{12,}",
                    no_match_message="Invalid email",
                )
            ]
        )


class TestServiceEmailConfigModel:
    @classmethod
    def setup_class(cls):
        cls.model = ServiceEmailConfigModel

    def test_str(self):
        config = ServiceEmailConfigModel(service=ServiceModel(name="squirrel"))

        assert str(config) == "squirrel's Email Config"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Service Email Config"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Service Email Configs"

    def test_meta_unique_together(self):
        assert self.model._meta.unique_together == (
            ("email_config_type", "service"),
        )

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model == ServiceModel
        assert field.verbose_name == "Service"
        assert field.remote_field.related_name == "email_configs"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_email_config_type_field(self):
        field = self.model._meta.get_field("email_config_type")

        assert type(field) == models.CharField
        assert field.max_length == 255
        assert (
            field.choices == ServiceEmailConfigModel.EMAIL_CONFIG_TYPE_CHOICES
        )

    def test_email_html_template_field(self):
        field = self.model._meta.get_field("email_html_template")

        assert type(field) == models.TextField
        assert field.verbose_name == "HTML Template"

    def test_email_subject_field(self):
        field = self.model._meta.get_field("email_subject")

        assert type(field) == models.CharField
        assert field.max_length == 255
        assert field.verbose_name == "Subject"

    def test_email_link_field(self):
        field = self.model._meta.get_field("email_link")

        assert type(field) == models.URLField
        assert field.verbose_name == "Link"

    def test_email_link_expiration_field(self):
        field = self.model._meta.get_field("email_link_expiration")

        assert type(field) == models.PositiveSmallIntegerField
        assert field.verbose_name == "Link Time Expiration"
        assert field.default == 1

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 10


class TestServiceCredentialConfigModel:
    @classmethod
    def setup_class(cls):
        cls.model = ServiceCredentialConfigModel

    def test_str(self):
        config = ServiceCredentialConfigModel(
            field="foo", credential_config_type="register"
        )

        assert str(config) == "foo's register config"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Service Credential Config"

    def test_meta_verbose_name_plural(self):
        assert (
            self.model._meta.verbose_name_plural
            == "Service Credential Configs"
        )

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model == ServiceModel
        assert field.remote_field.related_name == "credential_configs"
        assert field.verbose_name == "Service"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_credential_config_type_field(self):
        field = self.model._meta.get_field("credential_config_type")

        assert type(field) == models.CharField
        assert field.max_length == 255
        assert field.verbose_name == "Credential Config Type"
        assert field.choices == self.model.CREDENTIAL_CONFIG_TYPES_CHOICES

    def test_field_field(self):
        field = self.model._meta.get_field("field")

        assert type(field) == models.CharField
        assert field.max_length == 255
        assert field.verbose_name == "Field"

    def test_label_field(self):
        field = self.model._meta.get_field("label")

        assert type(field) == models.CharField
        assert field.max_length == 255
        assert field.verbose_name == "Label"

    def test_field_html_type_field(self):
        field = self.model._meta.get_field("field_html_type")

        assert type(field) == models.CharField
        assert field.max_length == 255
        assert field.verbose_name == "HTML Type"
        assert field.choices == self.model.HTML_TYPE_CHOICES
        assert field.null is True
        assert field.blank is True

    def test_rule_field(self):
        field = self.model._meta.get_field("rule")

        assert type(field) == models.CharField
        assert field.max_length == 255
        assert field.verbose_name == "Field Rule"
        assert field.help_text == "A Regex to validate this field"
        assert field.null is True
        assert field.blank is True

    def test_no_match_message_field(self):
        field = self.model._meta.get_field("no_match_message")

        assert type(field) == models.CharField
        assert field.max_length == 255
        assert field.verbose_name == "Error Message"
        assert field.help_text == (
            "The message that will be shown when the value"
            " entered in this field does not match the field rule"
        )
        assert field.null is True
        assert field.blank is True
