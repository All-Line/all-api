from unittest.mock import Mock, patch

from pipelines.base import BasePipeItem
from pipelines.items import SendEmail


class TestSendEmail:
    @classmethod
    def setup_class(cls):
        cls.item = SendEmail

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    def test_get_email_config_without_user_guest(self):
        mock_pipeline = Mock(user=Mock(is_guest=False))
        pipe_item = self.item(mock_pipeline)
        pipe_item._get_email_config(mock_pipeline.user)

        mock_service = mock_pipeline.user.service
        mock_service.email_configs.filter.assert_called_once_with(
            email_config_type=mock_pipeline.email_type
        )

        mock_service.email_configs.filter.return_value.first.assert_called_once()

    def test_get_email_config_with_user_guest(self):
        mock_pipeline = Mock(user=Mock(is_guest=True))
        pipe_item = self.item(mock_pipeline)
        email_config = pipe_item._get_email_config(mock_pipeline.user)

        mock_event = mock_pipeline.user.event
        mock_event.email_configs.filter.assert_called_once_with(
            email_config_type=mock_pipeline.email_type
        )

        mock_event.email_configs.filter.return_value.first.assert_called_once()

        assert email_config == (
            mock_event.email_configs.filter.return_value.first.return_value
        )

    def test_get_email_from_without_user_guest(self):
        mock_pipeline = Mock(user=Mock(is_guest=False))
        pipe_item = self.item(mock_pipeline)
        email_from = pipe_item._get_email_from(mock_pipeline.user)

        mock_service = mock_pipeline.user.service
        assert email_from == mock_service.smtp_email

    def test_get_email_from_with_user_guest(self):
        mock_pipeline = Mock(user=Mock(is_guest=True))
        pipe_item = self.item(mock_pipeline)
        email_from = pipe_item._get_email_from(mock_pipeline.user)

        mock_event = mock_pipeline.user.event
        assert email_from == mock_event.smtp_email

    def test_get_user_html_keys(self):
        mock_user = Mock()
        pipe_item = self.item(Mock())

        html_keys = pipe_item._get_user_html_keys(mock_user)

        assert html_keys == {
            "FIRST_NAME": mock_user.first_name,
            "LAST_NAME": mock_user.last_name,
            "USERNAME": mock_user.username,
            "EMAIL": mock_user.email,
            "TOKEN": pipe_item.pipeline.token,
            "SERVICE_NAME": mock_user.service.name,
            "EVENT_NAME": mock_user.event.title,
            "GUEST_PASSWORD": pipe_item.pipeline.password,
        }

    @patch.object(SendEmail, "_get_email_config")
    @patch.object(SendEmail, "_get_email_from")
    @patch.object(SendEmail, "_get_user_html_keys")
    def test_run(
        self, mock_get_user_html_keys, mock_get_email_from, mock_get_email_config
    ):
        pipe_item = self.item(Mock())
        pipe_item._run()

        mock_pipeline = pipe_item.pipeline
        mock_user = mock_pipeline.user

        mock_get_email_config.assert_called_once_with(mock_user)
        mock_get_email_from.assert_called_once_with(mock_user)

        mock_email_config = mock_get_email_config.return_value

        mock_get_user_html_keys.assert_called_once_with(mock_user)

        mock_email_config.send_email.assert_called_once_with(
            from_email=mock_get_email_from.return_value,
            to_emails=[mock_user.email],
            html_keys=mock_get_user_html_keys.return_value,
        )
