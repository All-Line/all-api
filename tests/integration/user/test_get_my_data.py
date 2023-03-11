import pytest


@pytest.mark.django_db
class TestGetMyData:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/user/me/"

    def test_get_my_data_failure_with_unauthenticated(self, api_client):
        path = self.endpoint
        response = api_client.get(path)

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_get_my_data_successfully(self, dummy_client_logged, dummy_user):
        path = self.endpoint
        response = dummy_client_logged.get(path)

        assert response.status_code == 200
        assert response.json() == {
            "birth_date": None,
            "country": None,
            "date_joined": (
                f"{dummy_user.date_joined.date()}T{dummy_user.date_joined.time()}Z"
            ),
            "profile_image": None,
            "first_name": "some first_name",
            "id": dummy_user.id,
            "is_premium": False,
            "is_verified": False,
            "last_name": "some last_name",
            "service": "dummy",
            "username": "dummy",
        }
