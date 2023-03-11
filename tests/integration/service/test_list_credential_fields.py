import pytest


@pytest.mark.django_db
class TestListCredentialFields:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/service/{service_slug}/credential-fields/{type}/"

    def test_list_credential_config_failure_due_to_invalid_credential_config_type(
        self, api_client, dummy_service
    ):
        path = self.endpoint.format(
            service_slug=dummy_service.slug, type="invalid_type"
        )
        response = api_client.get(path)

        assert response.status_code == 404

    def test_list_credential_config_failure_due_to_invalid_service_slug(
        self,
        api_client,
    ):
        path = self.endpoint.format(service_slug="foo", type="login")
        response = api_client.get(path)

        assert response.status_code == 404

    def test_list_credential_config_login(self, api_client, dummy_service):
        path = self.endpoint.format(service_slug=dummy_service.slug, type="login")
        response = api_client.get(path)

        credential_config = dummy_service.credential_configs.filter(
            credential_config_type="login"
        )

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": credential_config[0].id,
                "credential_config_type": credential_config[0].credential_config_type,
                "field": credential_config[0].field,
                "label": credential_config[0].label,
                "field_html_type": credential_config[0].field_html_type,
                "rule": credential_config[0].rule,
                "no_match_message": credential_config[0].no_match_message,
            },
            {
                "id": credential_config[1].id,
                "credential_config_type": credential_config[1].credential_config_type,
                "field": credential_config[1].field,
                "label": credential_config[1].label,
                "field_html_type": credential_config[1].field_html_type,
                "rule": credential_config[1].rule,
                "no_match_message": credential_config[1].no_match_message,
            },
        ]

    def test_list_credential_config_register(self, api_client, dummy_service):
        path = self.endpoint.format(service_slug=dummy_service.slug, type="register")
        response = api_client.get(path)

        credential_config = dummy_service.credential_configs.filter(
            credential_config_type="register"
        )

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": credential_config[0].id,
                "credential_config_type": credential_config[0].credential_config_type,
                "field": credential_config[0].field,
                "label": credential_config[0].label,
                "field_html_type": credential_config[0].field_html_type,
                "rule": credential_config[0].rule,
                "no_match_message": credential_config[0].no_match_message,
            },
            {
                "id": credential_config[1].id,
                "credential_config_type": credential_config[1].credential_config_type,
                "field": credential_config[1].field,
                "label": credential_config[1].label,
                "field_html_type": credential_config[1].field_html_type,
                "rule": credential_config[1].rule,
                "no_match_message": credential_config[1].no_match_message,
            },
            {
                "id": credential_config[2].id,
                "credential_config_type": credential_config[2].credential_config_type,
                "field": credential_config[2].field,
                "label": credential_config[2].label,
                "field_html_type": credential_config[2].field_html_type,
                "rule": credential_config[2].rule,
                "no_match_message": credential_config[2].no_match_message,
            },
        ]
