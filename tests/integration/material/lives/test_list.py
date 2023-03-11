import pytest
from django.utils import timezone

from tests.factories.live import LiveFactory


@pytest.mark.django_db
class TestListLives:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/live/"

    def test_list_lives_failure_unauthenticated(self, api_client):
        path = self.endpoint
        response = api_client.get(path)

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_list_live_successfully(self, dummy_client_logged, live):
        LiveFactory(starts_at=timezone.now() - timezone.timedelta(days=1))
        path = self.endpoint
        response = dummy_client_logged.get(path)

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json() == [
            {
                "id": live.id,
                "title": live.title,
                "description": live.description,
                "slug": live.slug,
                "is_paid": live.is_paid,
                "starts_at": f"{live.starts_at.date()}T{live.starts_at.time()}Z",
                "integration_field": live.integration_field,
                "live_type": live.live_type,
                "image": None,
            }
        ]
