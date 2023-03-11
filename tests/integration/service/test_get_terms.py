import pytest


@pytest.mark.django_db
class TesteGetTerms:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/service/{slug}/terms/"

    def test_terms_failure_not_found_service(self, api_client):
        path = self.endpoint.format(slug="foo")
        response = api_client.get(path)

        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_terms_successfully(self, api_client, dummy_service):
        path = self.endpoint.format(slug=dummy_service.slug)
        response = api_client.get(path)

        assert response.status_code == 200
        assert response.json() == {"terms": dummy_service.terms}
