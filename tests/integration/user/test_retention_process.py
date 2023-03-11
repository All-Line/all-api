import pytest

from tests.factories.token import TokenFactory


@pytest.mark.django_db
class TestRetentionProcess:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/user/delete_me/"

    def test_retention_process_failure_unauthenticated(self, api_client):
        path = self.endpoint
        data = {"delete_reason": "foo bar"}
        response = api_client.delete(path, data)

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_retention_process_failure_without_required_field(
        self, dummy_client_logged
    ):
        path = self.endpoint
        response = dummy_client_logged.delete(path, {})

        assert response.status_code == 400
        assert response.json() == {"delete_reason": ["This field is required."]}

    def test_retention_process_failure_with_invalid_delete_reason(
        self, dummy_client_logged
    ):
        path = self.endpoint
        data = {"delete_reason": "foo bar"}
        response = dummy_client_logged.delete(path, data)

        assert response.status_code == 400
        assert response.json() == {"delete_reason": ["delete_reason"]}

    def test_retention_process_failure_with_user_already_deleted(self, api_client):
        path = self.endpoint
        data = {"delete_reason": "foo bar bas"}
        token = TokenFactory()
        user = token.user
        user.is_active = False
        user.is_deleted = True
        user.save()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.delete(path, data)

        assert response.status_code == 401
        assert response.json() == {"detail": "User inactive or deleted."}

    def test_retention_process_successfully(self, dummy_client_logged):
        path = self.endpoint
        data = {"delete_reason": "foo bar bas"}
        response = dummy_client_logged.delete(path, data)

        assert response.status_code == 204
