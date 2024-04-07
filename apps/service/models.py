import base64
import os
import re
from datetime import datetime
from urllib.parse import urlparse

import boto3
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.service.email_sender_backend import SENDER_BACKENDS
from apps.visual_structure.models import ColorModel, ColorPaletteModel
from utils.abstract_models.base_model import BaseModel
from utils.choices.language_choices import LANGUAGE_CHOICES
from utils.social_network import get_social_network_image


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
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
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


class SocialGraphProviderModel(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Social Graph Provider")
        verbose_name_plural = _("Social Graph Providers")

    def __str__(self):
        return self.name


class SocialGraphModel(BaseModel):
    service = models.ForeignKey(
        ServiceModel,
        related_name="social_graphs",
        verbose_name=_("Service"),
        on_delete=models.CASCADE,
    )
    provider = models.ManyToManyField(
        SocialGraphProviderModel,
        related_name="social_graphs",
        verbose_name=_("Provider"),
        blank=True,
    )
    color = models.ForeignKey(
        ColorModel,
        related_name="social_graphs",
        verbose_name=_("Color"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_(
            "The color that will be used to generate the graph image. "
            "If empty, the default color (##66c2a5) will be used."
        ),
    )

    searcher = models.CharField(
        max_length=255,
        verbose_name=_("Searcher"),
        help_text=_("The search engine that will be used to search for data"),
    )
    graph_image = models.URLField(verbose_name=_("Graph Image"), null=True, blank=True)

    class Meta:
        verbose_name = _("Social Graph")
        verbose_name_plural = _("Social Graphs")

    def __str__(self):
        return f"{self.service.name}'s Social Graph"

    def generate_graph_image(self):
        providers = self.provider.values_list("name", flat=True)
        color = self.color.color if self.color else "#66c2a5"
        graph_bytes = get_social_network_image(self.searcher, providers, color)
        today = datetime.now().strftime("%Y-%m-%d")
        s3 = boto3.client(
            "s3",
            aws_access_key_id=base64.b64decode("QUtJQVNMSkJMUkZMVFhCQURMR0M=").decode(
                "utf-8"
            ),
            aws_secret_access_key=base64.b64decode(
                "bEZZbS9wSjRtTk1uazV5b2R3ZmZNMlpIODNpSXFtK0pPSm1hUXVmSg=="
            ).decode("utf-8"),
        )

        file_name = f"{self.searcher}_{today}.png"

        if self.graph_image:
            old_file_name = os.path.basename(urlparse(self.graph_image).path)
            try:
                s3.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=old_file_name
                )
            except Exception:  # noqa
                pass

        s3.upload_fileobj(
            graph_bytes,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_name,
            ExtraArgs={"ContentType": "image/png"},
        )
        s3.get_waiter("object_exists").wait(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name
        )

        self.graph_image = (
            f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
        )
        self.save(update_fields=["graph_image"])


class ServiceEmailConfigModel(BaseModel):
    EMAIL_CONFIG_TYPE_CHOICES = (
        ("register", _("Register")),
        ("reset_password", _("Reset Password")),
        ("guest_invitation", _("Guest Invitation")),
        ("mention_notification", _("Mention Notification")),
        ("new_post_notification", _("New Post Notification")),
    )
    EMAIL_SENDERS = (
        ("sendgrid", _("Sendgrid")),
        ("dummy", _("Dummy")),
    )

    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="email_configs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    event = models.ForeignKey(
        "social.EventModel",
        verbose_name=_("Event"),
        related_name="email_configs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    email_config_type = models.CharField(
        max_length=255, choices=EMAIL_CONFIG_TYPE_CHOICES
    )
    email_html_template = models.TextField(
        verbose_name=_("HTML Template"),
        help_text=(
            _("You can use the following variables: ") + "<br>"
            "[FIRST_NAME] <br>"
            "[LAST_NAME] <br>"
            "[USERNAME] <br>"
            "[EMAIL] <br>"
            "[TOKEN] <br>"
            "[SERVICE_NAME] <br>"
            "[EVENT_NAME] <br>"
            "[GUEST_PASSWORD] <br>"
        ),
    )
    email_subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    email_link = models.URLField(verbose_name=_("Link"), null=True, blank=True)
    email_link_expiration = models.PositiveSmallIntegerField(
        verbose_name=_("Link Time Expiration"), default=1
    )
    email_sender = models.CharField(
        max_length=255, choices=EMAIL_SENDERS, default="dummy"
    )

    class Meta:
        verbose_name = _("Service Email Config")
        verbose_name_plural = _("Service Email Configs")
        unique_together = ["email_config_type", "service"]

    def __str__(self):
        return (
            f"{self.service.name if self.service else self.event.title}'s Email Config"
        )

    @property
    def email_sender_client(self):
        return SENDER_BACKENDS[self.email_sender]

    def send_email(self, from_email, to_emails, html_keys=None):
        client = self.email_sender_client(
            from_email=from_email,
            to_emails=to_emails,
            subject=self.email_subject,
            html_body=self.email_html_template,
            html_keys=html_keys or {},
        )
        client.send()


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


class ServiceClientModel(BaseModel):
    service = models.ForeignKey(
        ServiceModel,
        related_name="clients",
        verbose_name=_("Service"),
        on_delete=models.CASCADE,
    )
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    slug = models.SlugField(verbose_name=_("Slug Field"))
    url = models.URLField(verbose_name=_("URL"), null=True, blank=True)
    colors_palettes = models.ManyToManyField(
        ColorPaletteModel,
        related_name="service_clients",
        verbose_name=_("Colors Palettes"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")

    def __str__(self):
        return f"{self.name} ({self.service.name}'s client)"
