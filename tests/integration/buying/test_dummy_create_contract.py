import pytest


@pytest.mark.django_db
class TestDummyCreateContract:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/contract/"

    def test_dummy_create_contract_failure_unauthenticated(self, api_client):
        path = self.endpoint
        response = api_client.post(path)

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_dummy_create_contract_failure_without_required_fields(
        self, dummy_client_logged, package
    ):
        path = self.endpoint
        response = dummy_client_logged.post(path, {})

        assert response.status_code == 400
        assert response.json() == {
            "receipt": ["This field is required."],
            "package": ["This field is required."],
        }

    def test_dummy_create_contract_failure_invalid_receipt(
        self, dummy_client_logged, package
    ):
        path = self.endpoint
        data = {
            "package": package.slug,
            "receipt": "some_receipt",
        }
        response = dummy_client_logged.post(path, data)

        assert response.status_code == 400
        assert response.json() == {"non_field_errors": ["Something went wrong."]}

    def test_dummy_create_contract_successfully(
        self, dummy_client_logged, package, dummy_user
    ):
        path = self.endpoint
        data = {
            "package": package.slug,
            "receipt": "dummy_receipt",
        }
        response = dummy_client_logged.post(path, data)

        dummy_user.refresh_from_db()
        assert response.status_code == 201
        assert response.json() == {"package": package.slug}
        assert dummy_user.is_premium is True
        assert len(dummy_user.contracts.all()) == 1
