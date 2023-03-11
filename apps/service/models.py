import re

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.visual_structure.models import ColorPaletteModel
from utils.abstract_models.base_model import BaseModel
from utils.choices.language_choices import LANGUAGE_CHOICES


class ServiceModel(BaseModel):

    name = models.CharField(verbose_name=_("Name"), max_length=255)
    slug = models.SlugField(verbose_name=_("Slug Field"))
    url = models.URLField(verbose_name=_("URL"), null=True, blank=True)
    smtp_email = models.EmailField(verbose_name=_("SMTP Email"), null=True, blank=True)
    colors_palettes = models.ManyToManyField(
        ColorPaletteModel,
        related_name="services",
        verbose_name=_("Colors Palettes"),
        blank=True,
    )
    confirmation_required = models.BooleanField(
        verbose_name=_("Confirmation Required"),
        default=True,
        help_text=(
            "If it's true, users need to confirm "
            "their e-mails to use the application."
        ),
    )
    language = models.CharField(
        verbose_name=_("Language"), max_length=255, choices=LANGUAGE_CHOICES
    )
    terms = models.TextField(
        verbose_name=_("Terms and Conditions"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self):
        return self.slug

    def validate_credential_fields(self, request_data, credential_config_type):
        credential_configs = self.credential_configs.only(
            "field", "rule", "no_match_message"
        ).filter(credential_config_type=credential_config_type)

        for config in credential_configs.iterator():
            field = config.field
            value = request_data.get(field, "")
            rule = config.rule

            if not value:
                raise ValidationError({field: [_("This field is required.")]})

            if rule:
                rule_doesnt_match = rule is not None and not re.match(rf"{rule}", value)

                if rule_doesnt_match:
                    raise ValidationError({field: config.no_match_message})

    def has_credential_configs(self):
        return self.credential_configs.count() != 0

    def clean(self):
        if self.has_credential_configs():
            login_configs = self.credential_configs.filter(
                credential_config_type="login"
            )
            register_configs = self.credential_configs.filter(
                credential_config_type="register"
            )

            login_has_password_field = (
                login_configs.filter(field="password").count() == 1
            )
            register_has_password_field = (
                register_configs.filter(field="password").count() == 1
            )

            if (login_configs.count() < 2 or register_configs.count() < 2) or not (
                login_has_password_field or register_has_password_field
            ):
                raise ValidationError(
                    _(
                        "Invalid credentials configuration. At least one email and "
                        "password configuration is required for both contexts."
                    )
                )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if not self.has_credential_configs():
            for config in settings.DEFAULT_CREDENTIAL_CONFIGS:
                ServiceCredentialConfigModel.objects.create(service=self, **config)


class ServiceEmailConfigModel(BaseModel):
    EMAIL_CONFIG_TYPE_CHOICES = (
        ("register", _("Register")),
        ("reset_password", _("Reset Password")),
    )

    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="email_configs",
        on_delete=models.CASCADE,
    )

    email_config_type = models.CharField(
        max_length=255, choices=EMAIL_CONFIG_TYPE_CHOICES
    )
    email_html_template = models.TextField(verbose_name=_("HTML Template"))
    email_subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    email_link = models.URLField(verbose_name=_("Link"))
    email_link_expiration = models.PositiveSmallIntegerField(
        verbose_name=_("Link Time Expiration"), default=1
    )

    def __str__(self):
        return f"{self.service.name}'s Email Config"

    class Meta:
        verbose_name = _("Service Email Config")
        verbose_name_plural = _("Service Email Configs")
        unique_together = ["email_config_type", "service"]


class ServiceCredentialConfigModel(BaseModel):
    CREDENTIAL_CONFIG_TYPES_CHOICES = (
        ("register", _("Register")),
        ("login", _("Login")),
    )
    HTML_TYPE_CHOICES = (
        ("email", _("Email")),
        ("number", _("Number")),
        ("password", _("Password")),
        ("tel", _("Tel")),
        ("text", _("Text")),
    )

    service = models.ForeignKey(
        ServiceModel,
        related_name=_("credential_configs"),
        verbose_name=_("Service"),
        on_delete=models.CASCADE,
    )
    credential_config_type = models.CharField(
        max_length=255,
        verbose_name=_("Credential Config Type"),
        choices=CREDENTIAL_CONFIG_TYPES_CHOICES,
    )
    field = models.CharField(max_length=255, verbose_name=_("Field"))
    label = models.CharField(max_length=255, verbose_name=_("Label"))
    field_html_type = models.CharField(
        max_length=255,
        verbose_name=_("HTML Type"),
        choices=HTML_TYPE_CHOICES,
        null=True,
        blank=True,
    )
    rule = models.CharField(
        max_length=255,
        verbose_name=_("Field Rule"),
        help_text=_("A Regex to validate this field"),
        null=True,
        blank=True,
    )
    no_match_message = models.CharField(
        max_length=255,
        verbose_name=_("Error Message"),
        help_text=_(
            "The message that will be shown when the value"
            " entered in this field does not match the field rule"
        ),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Service Credential Config")
        verbose_name_plural = _("Service Credential Configs")

    def __str__(self):
        return f"{self.field}'s {self.credential_config_type} config"
