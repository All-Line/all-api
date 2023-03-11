import pytest


@pytest.mark.django_db
class TestServiceDetail:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/service/{service_slug}/"

    def test_get_service_by_slug_failure_with_service_not_found(self, api_client):
        path = self.endpoint.format(service_slug="foo")
        response = api_client.get(path=path)

        assert response.status_code == 404
        assert response.data == {"detail": "Not found."}

    def test_get_service_by_slug_successfully(
        self, api_client, dummy_service, color_palette
    ):
        path = self.endpoint.format(service_slug=dummy_service.slug)
        response = api_client.get(path=path)

        assert response.status_code == 200
        assert response.json() == {
            "id": dummy_service.id,
            "is_active": dummy_service.is_active,
            "name": dummy_service.name,
            "slug": dummy_service.slug,
            "url": dummy_service.url,
            "colors_palettes": [
                {
                    "id": color_palette.id,
                    "is_active": color_palette.is_active,
                    "title": color_palette.title,
                    "description": color_palette.description,
                    "colors": [
                        {
                            "title": color_palette.colors.all()[0].title,
                            "color": color_palette.colors.all()[0].color,
                        },
                        {
                            "title": color_palette.colors.all()[1].title,
                            "color": color_palette.colors.all()[1].color,
                        },
                    ],
                }
            ],
            "confirmation_required": dummy_service.confirmation_required,
            "language": dummy_service.language,
            "terms": dummy_service.terms,
        }
