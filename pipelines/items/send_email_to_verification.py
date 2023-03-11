from django.conf import settings
from django.core.mail import send_mail

from apps.service.email_templates.generic import GENERIC_HTML_TEMPLATE
from apps.service.models import ServiceEmailConfigModel
from pipelines.base import BasePipeItem


class SendEmailToVerification(BasePipeItem):
    @staticmethod
    def _build_template(template, keys):
        for key, value in keys.items():
            template = template.replace(key, value)

        return template

    @staticmethod
    def _get_keys(email_config, user, service):
        if email_config:
            return {
                "ACTIVATE_LINK_CONFIG": f"{email_config.email_link}{user.auth_token}/",
                "USER_NAME": f"{user.first_name} {user.last_name}",
                "SERVICE_NAME": service.name,
            }

        return {
            "TITLE": service.name,
            "USER_NAME": f"{user.first_name} {user.last_name}",
            "LINK": f"{service.url}{user.auth_token}/",
            "SERVICE_NAME": service.name,
            "ACTION": "register",
        }

    def _compile_email_template(self, email_config, user=None, service=None):
        template = getattr(email_config, "email_html_template", GENERIC_HTML_TEMPLATE)

        keys = self._get_keys(email_config, user, service)
        template = self._build_template(template, keys)

        return template

    @staticmethod
    def _get_email_config_or_none(service):
        try:
            email_config = service.email_configs.get(email_config_type="register")
            return email_config
        except ServiceEmailConfigModel.DoesNotExist:
            return None

    def _run(self):
        user = self.pipeline.user
        service = user.service

        email_config = self._get_email_config_or_none(service)
        email_to = getattr(settings, "DEV_EMAIL", user.email)

        template = self._compile_email_template(email_config, user, service)
        email_subject = getattr(email_config, "email_subject", "Start System")

        send_mail(
            email_subject,
            "",
            service.smtp_email,
            [email_to],
            fail_silently=True,
            html_message=template,
        )
