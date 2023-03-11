from unittest.mock import patch

from apps.buying.backends import AppleBackend
from apps.buying.backends.base import BaseBackend


class TestAppleBackend:
    @classmethod
    def setup_class(cls):
        cls.backend = AppleBackend()

    def test_parent_class(self):
        assert issubclass(AppleBackend, BaseBackend)

    @patch("apps.buying.backends.apple.requests")
    @patch("apps.buying.backends.apple.env")
    def test_is_valid_receipt(self, mock_env, mock_requests):
        valid_apple_status = 0
        mock_requests.post.return_value.json.return_value = {
            "status": valid_apple_status
        }
        result = self.backend._is_valid_receipt("some_receipt")

        mock_env.assert_called_once_with("APPLE_SHARED_SECRET")

        mock_requests.post.assert_called_once_with(
            "https://buy.itunes.apple.com/verifyReceipt",
            json={"receipt-data": "some_receipt", "password": mock_env.return_value},
        )

        assert result is True
