import pytest


@pytest.mark.django_db
class TestUpdateMe:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/user/update_me/"

    def test_update_me_failure_unauthenticated(self, api_client):
        path = self.endpoint
        response = api_client.patch(path)

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_update_successfully_with_unexpected_fields(
        self, dummy_client_logged, dummy_user, dummy_service
    ):
        path = self.endpoint
        data = {"foo": "foo", "bar": "barr"}
        response = dummy_client_logged.patch(path, data)

        assert response.status_code == 200
        assert response.json() == {
            "birth_date": None,
            "country": None,
            "profile_image": None,
            "date_joined": (
                f"{dummy_user.date_joined.date()}T{dummy_user.date_joined.time()}Z"
            ),
            "first_name": dummy_user.first_name,
            "id": dummy_user.id,
            "is_premium": False,
            "is_verified": False,
            "last_name": dummy_user.last_name,
            "service": dummy_service.slug,
            "username": dummy_user.username,
        }

    def test_update_successfully(self, dummy_client_logged, dummy_user, dummy_service):
        path = self.endpoint
        new_username = "foobar"
        data = {
            "username": new_username,
        }
        response = dummy_client_logged.patch(path, data)

        assert response.status_code == 200
        assert response.json() == {
            "birth_date": None,
            "country": None,
            "profile_image": None,
            "date_joined": (
                f"{dummy_user.date_joined.date()}T{dummy_user.date_joined.time()}Z"
            ),
            "first_name": dummy_user.first_name,
            "id": dummy_user.id,
            "is_premium": False,
            "is_verified": False,
            "last_name": dummy_user.last_name,
            "service": dummy_service.slug,
            "username": new_username,
        }
