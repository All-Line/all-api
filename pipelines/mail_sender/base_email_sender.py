from typing import List, Optional


class BaseEmailSender:
    def __init__(
        self,
        subject: str,
        html_body: str,
        from_email: str,
        to_emails: List[str],
        html_keys: Optional[dict] = None,
    ):
        self.subject = subject
        self.html_body = html_body
        self.from_email = from_email
        self.to_emails = to_emails
        self.html_keys = html_keys or {}

    def compile_html_body(self):
        html_keys = self.html_keys

        for key, value in html_keys.items():
            self.html_body = self.html_body.replace(f"[{key}]", value or "")

        return self.html_body

    def send(self):
        return self._send()

    def _send(self):
        raise NotImplementedError  # pragma: no cover
