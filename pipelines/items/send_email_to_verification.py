from pipelines.base import BasePipeItem


class SendEmail(BasePipeItem):
    def _get_email_config(self, user):
        email_config_context = user.service

        if user.is_guest:
            email_config_context = user.event

        return email_config_context.email_configs.filter(
            email_config_type=self.pipeline.email_type
        ).first()

    @staticmethod
    def _get_email_from(user):
        email_from = user.service.smtp_email

        if user.is_guest:
            email_from = user.event.smtp_email

        return email_from

    def _get_user_html_keys(self, user):
        return {
            "FIRST_NAME": user.first_name,
            "LAST_NAME": user.last_name,
            "USERNAME": user.username,
            "EMAIL": user.email,
            "TOKEN": getattr(self.pipeline, "token", ""),
            "SERVICE_NAME": user.service.name,
            "EVENT_NAME": user.event.title if user.event else None,
            "GUEST_PASSWORD": getattr(self.pipeline, "password", ""),
        }

    def _run(self):
        if self.pipeline.send_mail:
            user = self.pipeline.user
            email_config = self._get_email_config(user)
            email_from = self._get_email_from(user)

            email_config.send_email(
                from_email=email_from,
                to_emails=[user.email],
                html_keys=self._get_user_html_keys(user),
            )
