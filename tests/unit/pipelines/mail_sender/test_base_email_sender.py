from unittest.mock import patch

from pipelines.mail_sender.base_email_sender import BaseEmailSender


class TestBaseEmailSender:
    @classmethod
    def setup_class(cls):
        cls.sender = BaseEmailSender

    def test_init(self):
        sender = self.sender(
            subject="test",
            html_body="test",
            from_email="test",
            to_emails=["test"],
            html_keys={"test": "test"},
        )

        assert sender.subject == "test"
        assert sender.html_body == "test"
        assert sender.from_email == "test"
        assert sender.to_emails == ["test"]
        assert sender.html_keys == {"test": "test"}

    def test_compile_html_body(self):
        sender = self.sender(
            subject="test",
            html_body="[test]",
            from_email="test",
            to_emails=["test"],
            html_keys={"test": "test"},
        )

        assert sender.compile_html_body() == "test"

    @patch.object(BaseEmailSender, "_send")
    def test_send(self, mock_send):
        sender = self.sender(
            subject="test",
            html_body="[test]",
            from_email="test",
            to_emails=["test"],
            html_keys={"test": "test"},
        )

        result = sender.send()

        mock_send.assert_called_once()

        assert result == mock_send.return_value
