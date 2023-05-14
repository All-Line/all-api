from unittest.mock import patch

import pytest

from apps.social.chat_ai.dummy_text_ai import DummyClient, DummyTextAI


class TestDummyClient:
    def test_init(self):
        client = DummyClient("valid_dummy_test")

        assert client.dummy_key == "valid_dummy_test"

    def test_send_with_valid_dummy_key(self):
        client = DummyClient("valid_dummy_test")
        response = client.send("Dummy test")

        assert response == "Dummy response for Dummy test"

    def test_send_with_invalid_dummy_key(self):
        client = DummyClient("invalid_dummy_test")
        with pytest.raises(ValueError) as e:
            client.send("Dummy test")

        assert str(e.value) == "Invalid key"


class TestDummyTextAI:
    @patch("apps.social.chat_ai.dummy_text_ai.TextAI.__init__")
    def test_init(self, mock_super_init):
        DummyTextAI(pre_set="foo", message="bar")

        mock_super_init.assert_called_once_with("foo", "bar")

    @patch("apps.social.chat_ai.dummy_text_ai.DummyClient")
    def test_get_client(self, mock_dummy_client):
        text_ai = DummyTextAI()
        client = text_ai.get_client()

        mock_dummy_client.assert_called_once_with("valid_dummy_test")
        assert client == mock_dummy_client.return_value

    def test_get_message(self):
        text_ai = DummyTextAI()
        message = text_ai.get_message()

        assert message == "Dummy test"

    @patch.object(DummyTextAI, "get_client")
    def test_get_response(self, mock_get_client):
        text_ai = DummyTextAI()
        message = "some_message"

        response = text_ai._get_response(message)

        mock_get_client.assert_called_once()
        mock_client = mock_get_client.return_value

        mock_client.send.assert_called_once_with(message)

        assert response == mock_client.send.return_value
