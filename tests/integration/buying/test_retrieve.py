import pytest


@pytest.mark.django_db
class TestRetrievePackage:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/package/{slug}/"

    def test_retrieve_failure_unauthenticated(self, api_client):
        path = self.endpoint.format(slug="2")
        response = api_client.get(path)

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_retrieve_failure_package_not_found(self, dummy_client_logged):
        path = self.endpoint.format(slug="foo")
        response = dummy_client_logged.get(path)

        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_retrieve_successfully(self, dummy_client_logged, package):
        path = self.endpoint.format(slug=package.slug)
        response = dummy_client_logged.get(path)

        assert response.status_code == 200
        assert response.json() == {
            "id": package.id,
            "is_active": package.is_active,
            "price": package.price,
            "slug": package.slug,
        }
