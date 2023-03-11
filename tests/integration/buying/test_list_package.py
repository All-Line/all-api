import pytest


@pytest.mark.django_db
class TestListPackage:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/package/"

    def test_list_packages_failure_unauthenticated(self, api_client):
        path = self.endpoint
        response = api_client.get(path)

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_list_packages_successfully(self, dummy_client_logged, package):
        path = self.endpoint
        response = dummy_client_logged.get(path)

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": package.id,
                "is_active": package.is_active,
                "price": package.price,
                "slug": package.slug,
            }
        ]
