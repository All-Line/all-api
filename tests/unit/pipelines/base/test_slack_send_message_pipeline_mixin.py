from unittest.mock import patch

from django.conf import settings

from pipelines.base import SlackMessagePipelineMixin


class TestSlackMessagePipelineMixin:
    @patch("pipelines.base.getattr")
    def test_init(self, mock_getattr):
        slack_message = SlackMessagePipelineMixin()

        mock_getattr.assert_called_once_with(settings, "SLACK_MESSAGE_URL", None)
        assert slack_message.emojis == {
            "check": "✅",
            "fail": "❌",
            "star": "⭐",
            "bug_1": "🪲",
            "bug_2": "🐞",
            "smile": "😁",
            "like": "👍",
            "robot": "🤖",
            "lock": "🔒",
            "biceps": "💪",
            "money": "💰",
        }
        assert slack_message.slack_message == ""
        assert slack_message.slack_message_url == mock_getattr.return_value

    def test_bold_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.bold(value)

        assert result == f"*{value}*"

    def test_italic_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.italic(value)

        assert result == f"_{value}_"

    def test_italic_bold_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.italic_bold(value)

        assert result == f"_*{value}*_"

    def test_scratched_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.scratched(value)

        assert result == f"~{value}~"

    def test_code_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.code(value)

        assert result == f"`{value}`"

    def test_block_code_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.block_code(value)

        assert result == f"\n ```{value}``` \n"

    def test_block_quote_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.block_quote(value)

        assert result == f"> {value}"

    def test_ordered_list_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.ordered_list_item(value)

        assert result == f"1. {value}"

    def test_bulleted_list_method(self):
        value = "test"
        result = SlackMessagePipelineMixin.bulleted_list_item(value)

        assert result == f"* {value}"

    def test_link_message_method(self):
        value = "test"
        url = "https://some_url/"
        result = SlackMessagePipelineMixin.link_message(url, value)

        assert result == f"<{url}|{value}>"
