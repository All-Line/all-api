from pipelines.mail_sender.base_email_sender import BaseEmailSender


class DummySender(BaseEmailSender):
    def _send(self):
        return {
            "status": "success",
            "message": "Email sent successfully",
            "data": {
                "subject": self.subject,
                "html_body": self.html_body,
                "from_email": self.from_email,
                "to_emails": self.to_emails,
                "html_keys": self.html_keys,
            },
            "compiled_html_body": self.compile_html_body(),
        }
