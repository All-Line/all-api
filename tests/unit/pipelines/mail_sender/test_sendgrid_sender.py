from unittest.mock import patch

from pipelines.mail_sender.sendgrid_sender import SendGridSender


class TestSendGridSender:
    @patch.object(SendGridSender, "compile_html_body")
    @patch("pipelines.mail_sender.sendgrid_sender.SendGridAPIClient")
    @patch("pipelines.mail_sender.sendgrid_sender.Mail")
    @patch("pipelines.mail_sender.sendgrid_sender.env")
    def test_send(
        self, mock_env, mock_mail, mock_sendgrid_api_client, mock_compile_html_body
    ):
        sender = SendGridSender(
            subject="test",
            html_body="[test]",
            from_email="test",
            to_emails=["test"],
            html_keys={"test": "test"},
        )
        result = sender._send()

        mock_mail.assert_called_once_with(
            from_email=sender.from_email,
            to_emails=sender.to_emails,
            subject=sender.subject,
            html_content=mock_compile_html_body.return_value,
        )

        mock_env.assert_called_once_with("SENDGRID_API_KEY")

        mock_sendgrid_api_client.assert_called_once_with(mock_env.return_value)

        assert result == mock_sendgrid_api_client.return_value.send.return_value
