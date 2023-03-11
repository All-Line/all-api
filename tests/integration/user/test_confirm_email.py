from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestUserConfigEmail:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/user/confirm_email/{token}/"

    def test_confirm_email_failure_due_to_token_does_not_exists(self, api_client):
        path = self.endpoint.format(token="foo")
        response = api_client.get(path)

        assert response.status_code == 410
        assert response.data == {"detail": "This link is expired"}

    def test_confirm_email_failure_due_to_token_is_expired(
        self, api_client, dummy_user, service_email_config_registration
    ):
        token = dummy_user.auth_token
        token.created = timezone.now() - timedelta(hours=2)
        token.save()

        path = self.endpoint.format(token=token)
        response = api_client.get(path)

        assert response.status_code == 410
        assert response.data == {"detail": "This link is expired"}

    def test_confirm_email_successfully(
        self, api_client, dummy_user, service_email_config_registration
    ):
        path = self.endpoint.format(token=dummy_user.auth_token)
        response = api_client.get(path)

        assert response.status_code == 204
