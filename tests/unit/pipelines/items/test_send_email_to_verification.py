from unittest.mock import Mock, patch

from apps.service.email_templates.generic import GENERIC_HTML_TEMPLATE
from apps.service.models import ServiceEmailConfigModel
from pipelines.base import BasePipeItem
from pipelines.items import SendEmailToVerification


class TestSendEmailToVerification:
    @classmethod
    def setup_class(cls):
        cls.item = SendEmailToVerification

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    def test_build_template(self):
        mock_template = "<p>FOO</p>"
        keys = {"FOO": "bar"}
        pipeline = Mock()
        item = self.item(pipeline)
        result = item._build_template(mock_template, keys)

        assert result == "<p>bar</p>"

    def test_get_keys_without_email_config(self):
        pipeline = Mock()
        user = pipeline.user
        service = user.service
        item = self.item(pipeline)
        result = item._get_keys(None, user, service)

        assert result == {
            "TITLE": service.name,
            "USER_NAME": f"{user.first_name} {user.last_name}",
            "LINK": f"{service.url}{user.auth_token}/",
            "SERVICE_NAME": service.name,
            "ACTION": "register",
        }

    def test_get_keys_with_email_config(self):
        mock_email_config = Mock()
        pipeline = Mock()
        user = pipeline.user
        service = user.service
        item = self.item(pipeline)
        result = item._get_keys(mock_email_config, user, service)

        assert result == {
            "ACTIVATE_LINK_CONFIG": (
                f"{mock_email_config.email_link}{user.auth_token}/"
            ),
            "USER_NAME": f"{user.first_name} {user.last_name}",
            "SERVICE_NAME": service.name,
        }

    @patch(
        "pipelines.items.send_email_to_verification.SendEmailToVerification._get_keys"
    )
    @patch(
        "pipelines.items.send_email_to_verification."
        "SendEmailToVerification._build_template"
    )
    def test_compile_email_template_without_email_config(
        self, mock_build_template, mock_get_keys
    ):
        mock_user = "foo"
        mock_service = Mock()
        pipeline = Mock()
        item = self.item(pipeline)
        result = item._compile_email_template(None, mock_user, mock_service)

        mock_get_keys.assert_called_once_with(None, mock_user, mock_service)
        mock_build_template.assert_called_once_with(
            GENERIC_HTML_TEMPLATE, mock_get_keys.return_value
        )
        assert result == mock_build_template.return_value

    @patch(
        "pipelines.items.send_email_to_verification."
        "SendEmailToVerification._get_keys"
    )
    @patch(
        "pipelines.items.send_email_to_verification."
        "SendEmailToVerification._build_template"
    )
    def test_compile_email_template_with_email_config(
        self, mock_build_template, mock_get_keys
    ):
        html_template = """
            <p>ACTIVATE_LINK_CONFIG</p>
            <p>USER_NAME</p>
            <p>SERVICE_NAME</p>
        """
        mock_user = "foo"
        mock_service = Mock()
        mock_email_config = Mock(email_html_template=html_template)
        pipeline = Mock()
        item = self.item(pipeline)
        result = item._compile_email_template(
            mock_email_config, mock_user, mock_service
        )

        mock_get_keys.assert_called_once_with(
            mock_email_config, mock_user, mock_service
        )
        mock_build_template(html_template, mock_get_keys.return_value)
        assert result == mock_build_template.return_value

    def test_get_email_config_or_none_without_email_config(self):
        mock_service = Mock()
        email_config = mock_service.email_configs
        email_config.get.side_effect = ServiceEmailConfigModel.DoesNotExist()
        pipeline = Mock()
        item = self.item(pipeline)

        result = item._get_email_config_or_none(mock_service)

        mock_service.email_configs.get.assert_called_once_with(
            email_config_type="register"
        )
        assert result is None

    def test_get_email_config_or_none_with_email_config(self):
        mock_service = Mock()
        pipeline = Mock()
        item = self.item(pipeline)
        result = item._get_email_config_or_none(mock_service)

        mock_service.email_configs.get.assert_called_once_with(
            email_config_type="register"
        )
        assert result == mock_service.email_configs.get.return_value

    @patch(
        "pipelines.items.send_email_to_verification."
        "SendEmailToVerification._get_email_config_or_none"
    )
    @patch("pipelines.items.send_email_to_verification.send_mail")
    @patch(
        "pipelines.items.send_email_to_verification."
        "SendEmailToVerification._compile_email_template"
    )
    @patch("pipelines.items.send_email_to_verification.settings")
    def test_run_with_dev_email(
        self,
        mock_settings,
        mock_compile_email_template,
        mock_send_mail,
        mock_get_email_config_or_none,
    ):
        mock_settings.DEV_EMAIL = "some@email.com"
        pipeline = Mock()
        user = pipeline.user
        service = user.service
        item = self.item(pipeline)
        item._run()

        mock_get_email_config_or_none.assert_called_once_with(service)
        mock_compile_email_template.assert_called_once_with(
            mock_get_email_config_or_none.return_value, user, service
        )
        mock_send_mail.assert_called_once_with(
            mock_get_email_config_or_none.return_value.email_subject,
            "",
            service.smtp_email,
            ["some@email.com"],
            fail_silently=True,
            html_message=mock_compile_email_template.return_value,
        )

    @patch(
        "pipelines.items.send_email_to_verification."
        "SendEmailToVerification._get_email_config_or_none"
    )
    @patch("pipelines.items.send_email_to_verification.send_mail")
    @patch(
        "pipelines.items.send_email_to_verification."
        "SendEmailToVerification._compile_email_template"
    )
    @patch("pipelines.items.send_email_to_verification.settings")
    def test_run_without_dev_email(
        self,
        mock_settings,
        mock_compile_email_template,
        mock_send_mail,
        mock_get_email_config_or_none,
    ):
        del mock_settings.DEV_EMAIL
        pipeline = Mock()
        user = pipeline.user
        service = user.service
        service.email_configs = None
        item = self.item(pipeline)
        item._run()

        mock_get_email_config_or_none.assert_called_once_with(service)
        mock_compile_email_template.assert_called_once_with(
            mock_get_email_config_or_none.return_value, user, service
        )
        mock_send_mail.assert_called_once_with(
            mock_get_email_config_or_none.return_value.email_subject,
            "",
            service.smtp_email,
            [user.email],
            fail_silently=True,
            html_message=mock_compile_email_template.return_value,
        )
