from unittest.mock import patch

from pipelines.mail_sender.dummy_sender import DummySender


class TestDummySender:
    @patch.object(DummySender, "compile_html_body")
    def test_send(self, mock_compile_html_body):
        sender = DummySender(
            subject="test",
            html_body="[test]",
            from_email="test",
            to_emails=["test"],
            html_keys={"test": "test"},
        )
        result = sender._send()

        assert result == {
            "status": "success",
            "message": "Email sent successfully",
            "data": {
                "subject": sender.subject,
                "html_body": sender.html_body,
                "from_email": sender.from_email,
                "to_emails": sender.to_emails,
                "html_keys": sender.html_keys,
            },
            "compiled_html_body": mock_compile_html_body.return_value,
        }
