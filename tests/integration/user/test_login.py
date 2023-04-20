import pytest

from tests.factories.service_credential_config import (
    ServiceCredentialConfigFactory,
)


@pytest.mark.django_db
class TestUserLogin:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/user/login/"

    def test_login_failure_without_required_fields(self, api_client):
        path = self.endpoint
        response = api_client.post(path, {})

        assert response.status_code == 400
        assert response.json() == {
            "email": ["This field is required."],
            "password": ["This field is required."],
            "service": ["This field is required."],
        }

    def test_login_failure_service_does_not_exist(self, api_client):
        path = self.endpoint
        data = {
            "email": "some@email.com",
            "password": "1234",
            "service": "foo",
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {
            "service": ["Object with slug=foo does not exist."]
        }

    def test_login_failure_does_not_exist(self, api_client, dummy_service):
        path = self.endpoint
        data = {
            "email": "foo@bar.com",
            "password": "12345Aa@",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": ["The data entered is incorrect."]
        }

    def test_login_failure_due_to_bad_credentials(
        self, api_client, dummy_service, dummy_user
    ):
        path = self.endpoint
        data = {
            "email": "foo@bar.com",
            "password": "1234",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": ["The data entered is incorrect."]
        }

    def test_login_failure_due_to_user_not_verified(
        self, api_client, dummy_service, dummy_user
    ):
        path = self.endpoint
        data = {
            "email": dummy_user.email,
            "password": "12345Aa@",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": ["This account is not verified."]
        }

    def test_login_failure_due_to_required_extra_field(
        self, api_client, dummy_service, dummy_user
    ):
        service_credential_config = ServiceCredentialConfigFactory(
            field="foo", label="bar"
        )
        dummy_service.credential_configs.add(service_credential_config)
        dummy_service.save()
        path = self.endpoint
        data = {
            "email": dummy_user.email,
            "password": "12345Aa@",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"foo": ["This field is required."]}

    def test_login_successfully_with_extra_field(
        self, api_client, dummy_service, dummy_user
    ):
        service_credential_config = ServiceCredentialConfigFactory(
            field="document", rule=r"^\d{11,11}$", label="bar"
        )
        dummy_service.credential_configs.add(service_credential_config)
        dummy_service.save()
        dummy_user.is_verified = True
        dummy_user.document = "12312312312"
        dummy_user.save()
        path = self.endpoint
        data = {
            "email": dummy_user.email,
            "password": "12345Aa@",
            "document": "12312312312",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 200
        assert response.json() == {
            "birth_date": None,
            "country": None,
            "date_joined": (
                f"{dummy_user.date_joined.date()}T{dummy_user.date_joined.time()}Z"
            ),
            "email": dummy_user.email,
            "first_name": dummy_user.first_name,
            "id": dummy_user.id,
            "is_premium": False,
            "is_verified": True,
            "last_name": dummy_user.last_name,
            "service": dummy_service.slug,
            "token": dummy_user.auth_token.key,
        }

    def test_login_successfully(self, api_client, dummy_service, dummy_user):
        dummy_user.is_verified = True
        dummy_user.save()
        path = self.endpoint
        data = {
            "email": dummy_user.email,
            "password": "12345Aa@",
            "service": dummy_service.slug,
        }
        response = api_client.post(path, data)

        assert response.status_code == 200
        assert response.json() == {
            "birth_date": None,
            "country": None,
            "date_joined": (
                f"{dummy_user.date_joined.date()}T{dummy_user.date_joined.time()}Z"
            ),
            "email": dummy_user.email,
            "first_name": dummy_user.first_name,
            "id": dummy_user.id,
            "is_premium": False,
            "is_verified": True,
            "last_name": dummy_user.last_name,
            "service": dummy_service.slug,
            "token": dummy_user.auth_token.key,
        }
