from unittest.mock import patch

from apps.social.chat_ai import GPT3TextAI


class TestGPT3TextAI:
    @patch("apps.social.chat_ai.gpt3_text_ai.ChatGPT")
    @patch("apps.social.chat_ai.gpt3_text_ai.env")
    def test_get_client(self, mock_env, mock_chat_gpt):
        text_ai = GPT3TextAI("foo", "bar")
        client = text_ai.get_client()

        mock_env.assert_called_once_with("OPEN_AI_KEY")
        mock_chat_gpt.assert_called_once_with(mock_env.return_value)

        assert client == mock_chat_gpt.return_value

    def test_get_message(self):
        text_ai = GPT3TextAI("foo", "bar")
        message = text_ai.get_message()

        assert (
            message
            == f"""
            {text_ai.pre_set}

            {text_ai.message}
        """
        )

    @patch.object(GPT3TextAI, "get_client")
    def test_get_response(self, mock_get_client):
        text_ai = GPT3TextAI("foo", "bar")
        message = "some_message"

        response = text_ai._get_response(message)

        mock_get_client.assert_called_once()
        mock_client = mock_get_client.return_value

        mock_client.just_chat.assert_called_once_with(message, 0.1)

        assert response == mock_client.just_chat.return_value
