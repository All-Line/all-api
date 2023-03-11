from unittest.mock import patch

import pytest
from django.conf import settings
from rest_framework.authtoken.models import Token

from tests.factories.service import ServiceFactory
from tests.factories.service_credential_config import ServiceCredentialConfigFactory
from tests.factories.user import UserFactory


@pytest.mark.django_db
class TestUserRegistration:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/user/"

    def test_registration_failure_without_required_fields(self, api_client):
        path = self.endpoint
        response = api_client.post(path, {})

        assert response.status_code == 400
        assert response.data == {
            "first_name": ["This field is required."],
            "last_name": ["This field is required."],
            "email": ["This field is required."],
            "password": ["This field is required."],
            "confirm_password": ["This field is required."],
            "service": ["This field is required."],
        }

    def test_registration_failure_due_to_incorrect_confirm_password(
        self, api_client, dummy_service
    ):
        path = self.endpoint
        data = {
            "first_name": "test",
            "last_name": "1",
            "email": "test_1@gmail.com",
            "password": "12345Aa@",
            "confirm_password": "12345",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"password": ["The passwords doesn't match."]}

    def test_registration_failure_password_does_not_match_rule(
        self, api_client, dummy_service
    ):
        path = self.endpoint
        data = {
            "first_name": "test",
            "last_name": "1",
            "email": "test_1@gmail.com",
            "password": "12345Aa",
            "confirm_password": "12345Aa@",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"password": ["Invalid password"]}

    def test_registration_failure_email_does_not_match_rule(
        self, api_client, dummy_service
    ):
        path = self.endpoint
        data = {
            "first_name": "test",
            "last_name": "1",
            "email": "test_1@gmail",
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"email": ["Enter a valid email address."]}

    def test_registration_failure_with_service_not_found(self, api_client):
        path = self.endpoint
        data = {
            "first_name": "test",
            "last_name": "1",
            "email": "test_1@gmail.com",
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "service": "foo",
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"service": ["Object with slug=foo does not exist."]}

    def test_registration_failure_with_email_duplicated(
        self, api_client, dummy_service
    ):
        path = self.endpoint
        data = {
            "first_name": "test",
            "last_name": "1",
            "email": "test_1@gmail.com",
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "service": dummy_service.slug,
        }
        UserFactory(email="test_1@gmail.com", service=dummy_service)
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"user": ["A user with this email already exists."]}

    def test_registration_failure_due_to_required_extra_field(
        self, api_client, dummy_service
    ):
        service_credential_config = ServiceCredentialConfigFactory(
            field="foo",
            rule=r"^\d{11,11}$",
            label="bar",
            credential_config_type="register",
        )
        dummy_service.credential_configs.add(service_credential_config)
        dummy_service.save()
        path = self.endpoint
        data = {
            "first_name": "test",
            "last_name": "2",
            "email": "test_2@gmail.com",
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"foo": ["This field is required."]}

    def test_registration_failure_extra_field_does_not_match_rule(
        self, api_client, dummy_service
    ):
        service_credential_config = ServiceCredentialConfigFactory(
            field="foo",
            rule=r"^\d{11,11}$",
            label="bar",
            credential_config_type="register",
        )
        dummy_service.credential_configs.add(service_credential_config)
        dummy_service.save()
        path = self.endpoint
        data = {
            "first_name": "test",
            "last_name": "2",
            "email": "test_2@gmail.com",
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "foo": "1231231231",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"foo": ["Some no match message"]}

    @patch("pipelines.items.send_email_to_verification.send_mail")
    def test_registration_successfully_with_extra_field(
        self,
        mock_send_mail,
        api_client,
        dummy_service,
        service_email_config_registration,
    ):
        service_credential_config = ServiceCredentialConfigFactory(
            field="document",
            rule=r"^\d{11,11}$",
            label="bar",
            credential_config_type="register",
        )
        dummy_service.credential_configs.add(service_credential_config)
        dummy_service.save()
        email_config = service_email_config_registration
        path = self.endpoint
        data = {
            "first_name": "test",
            "last_name": "2",
            "email": "test_2@gmail.com",
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "document": "12312312312",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        token = Token.objects.first()

        mock_send_mail.assert_called_once_with(
            email_config.email_subject,
            "",
            dummy_service.smtp_email,
            [settings.DEV_EMAIL],
            fail_silently=True,
            html_message=email_config.email_html_template.replace(
                "ACTIVATE_LINK_CONFIG", f"{email_config.email_link}{token.key}/"
            )
            .replace("USER_NAME", "test 2")
            .replace("SERVICE_NAME", dummy_service.name),
        )
        assert response.status_code == 201
        assert response.json() == {
            "first_name": "test",
            "last_name": "2",
            "email": "test_2@gmail.com",
            "token": token.key,
            "service": "dummy",
            "birth_date": None,
            "country": None,
        }

    @patch("pipelines.items.send_email_to_verification.send_mail")
    def test_registration_successfully_with_birth_date(
        self,
        mock_send_mail,
        api_client,
        dummy_service,
        service_email_config_registration,
    ):
        email_config = service_email_config_registration
        path = self.endpoint
        data = {
            "first_name": "foo",
            "last_name": "bar",
            "email": "foobar@gmail.com",
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "service": dummy_service.slug,
            "birth_date": "1999-12-20",
        }
        response = api_client.post(path, data)

        token = Token.objects.first()

        mock_send_mail.assert_called_once_with(
            email_config.email_subject,
            "",
            dummy_service.smtp_email,
            [settings.DEV_EMAIL],
            fail_silently=True,
            html_message=email_config.email_html_template.replace(
                "ACTIVATE_LINK_CONFIG", f"{email_config.email_link}{token.key}/"
            )
            .replace("USER_NAME", "foo bar")
            .replace("SERVICE_NAME", dummy_service.name),
        )
        assert response.status_code == 201
        assert response.json() == {
            "first_name": "foo",
            "last_name": "bar",
            "email": "foobar@gmail.com",
            "token": token.key,
            "service": "dummy",
            "birth_date": "1999-12-20",
            "country": None,
        }

    @patch("pipelines.items.send_email_to_verification.send_mail")
    def test_registration_successfully_with_registration_in_another_service(
        self,
        mock_send_mail,
        api_client,
        dummy_service,
        service_email_config_registration,
    ):
        user_email = "foobar@gmail.com"
        email_config = service_email_config_registration
        service = ServiceFactory()
        UserFactory(email=user_email, service=service)

        path = self.endpoint
        data = {
            "first_name": "foo",
            "last_name": "bar",
            "email": user_email,
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "service": dummy_service.slug,
            "birth_date": "1999-12-20",
        }
        response = api_client.post(path, data)

        token = Token.objects.first()

        mock_send_mail.assert_called_once_with(
            email_config.email_subject,
            "",
            dummy_service.smtp_email,
            [settings.DEV_EMAIL],
            fail_silently=True,
            html_message=email_config.email_html_template.replace(
                "ACTIVATE_LINK_CONFIG", f"{email_config.email_link}{token.key}/"
            )
            .replace("USER_NAME", "foo bar")
            .replace("SERVICE_NAME", dummy_service.name),
        )
        assert response.status_code == 201
        assert response.json() == {
            "first_name": "foo",
            "last_name": "bar",
            "email": "foobar@gmail.com",
            "token": token.key,
            "service": dummy_service.slug,
            "birth_date": "1999-12-20",
            "country": None,
        }

    @patch("pipelines.items.send_email_to_verification.send_mail")
    def test_registration_successfully(
        self,
        mock_send_mail,
        api_client,
        dummy_service,
        service_email_config_registration,
    ):
        email_config = service_email_config_registration
        path = self.endpoint
        data = {
            "first_name": "foo",
            "last_name": "bar",
            "email": "foobar@gmail.com",
            "password": "12345Aa@",
            "confirm_password": "12345Aa@",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        token = Token.objects.first()

        mock_send_mail.assert_called_once_with(
            email_config.email_subject,
            "",
            dummy_service.smtp_email,
            [settings.DEV_EMAIL],
            fail_silently=True,
            html_message=email_config.email_html_template.replace(
                "ACTIVATE_LINK_CONFIG", f"{email_config.email_link}{token.key}/"
            )
            .replace("USER_NAME", "foo bar")
            .replace("SERVICE_NAME", dummy_service.name),
        )
        assert response.status_code == 201
        assert response.json() == {
            "first_name": "foo",
            "last_name": "bar",
            "email": "foobar@gmail.com",
            "token": token.key,
            "service": "dummy",
            "birth_date": None,
            "country": None,
        }
