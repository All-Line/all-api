from unittest.mock import Mock

from pipelines.base import get_class_name


def test_get_class_name():
    obj = Mock()
    obj.__name__ = "test"
    result = get_class_name(obj)

    assert result == "test"
