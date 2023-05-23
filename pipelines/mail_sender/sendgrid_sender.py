from decouple import config as env
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from pipelines.mail_sender.base_email_sender import BaseEmailSender


class SendGridSender(BaseEmailSender):
    def _send(self):
        message = Mail(
            from_email=self.from_email,
            to_emails=self.to_emails,
            subject=self.subject,
            html_content=self.compile_html_body(),
        )

        sg = SendGridAPIClient(env("SENDGRID_API_KEY"))
        return sg.send(message)
