import pytest

from apps.buying.backends import DummyBackend
from apps.buying.backends.base import BaseBackend


class TestDummyBackend:
    @classmethod
    def setup_class(cls):
        cls.backend = DummyBackend()

    def test_parent_class(self):
        assert issubclass(DummyBackend, BaseBackend)

    @pytest.mark.parametrize(
        "receipt,expected", (("dummy_receipt", True), ("invalid_receipt", False))
    )
    def test_is_valid_receipt(self, receipt, expected):
        result = self.backend._is_valid_receipt(receipt)

        assert result == expected
