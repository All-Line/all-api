from unittest.mock import patch

import pytest

from apps.buying.backends.base import BaseBackend


class TestBaseBackend:
    @classmethod
    def setup_class(cls):
        cls.base = BaseBackend()

    @patch("apps.buying.backends.base.jwt")
    def test_get_jwt(self, mock_jwt):
        result = self.base.get_jwt(
            {"key": "some_key"},
            "some_secret_key",
            "some_algorithm",
            {"alg": "some_alg"},
        )

        mock_jwt.encode.assert_called_once_with(
            {"key": "some_key"},
            "some_secret_key",
            "some_algorithm",
            {"alg": "some_alg"},
        )
        assert result == mock_jwt.encode.return_value

    def test__is_valid_receipt(self):
        with pytest.raises(NotImplementedError):
            self.base._is_valid_receipt("receipt")

    @patch("apps.buying.backends.base.BaseBackend._is_valid_receipt")
    def test_is_valid_receipt(self, mock_is_valid_receipt):
        result = self.base.is_valid_receipt("receipt")

        mock_is_valid_receipt.assert_called_once_with("receipt")
        assert result == mock_is_valid_receipt.return_value
