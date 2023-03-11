class TestPing:
    def test_ping(self, api_client):
        response = api_client.get("/api/v1/ping/")

        assert response.status_code == 200
        assert response.data == "pong"
