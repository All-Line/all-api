from unittest.mock import Mock, patch

from django.db import models

from apps.user.managers import UserForRetentionManager, UserManager


class TestUserForRetentionManager:
    @classmethod
    def setup_class(cls):
        cls.manager = UserForRetentionManager

    def test_parent_class(self):
        assert issubclass(self.manager, models.Manager)

    @patch("apps.user.managers.super")
    def test_get_queryset_static_method(self, mock_super):
        mock_args = Mock()
        mock_kwargs = Mock()
        result = self.manager.get_queryset(mock_args, mock_kwargs)
        queryset = mock_super.return_value.get_queryset.return_value

        queryset.filter.assert_called_once_with(is_deleted=True)
        assert (
            result
            == mock_super.return_value.get_queryset.return_value.filter.return_value
        )


class TestUserManager:
    @classmethod
    def setup_class(cls):
        cls.manager = UserManager

    def test_parent_class(self):
        assert issubclass(self.manager, models.Manager)

    @patch("apps.user.managers.super")
    def test_get_queryset_static_method(self, mock_super):
        args = [1, 2, 3]
        kwargs = {"foo": "bar"}
        result = self.manager.get_queryset(*args, **kwargs)
        queryset = mock_super.return_value.get_queryset.return_value
        queryset.filter.assert_called_once_with(is_active=True, is_deleted=False)
        assert (
            result
            == mock_super.return_value.get_queryset.return_value.filter.return_value
        )
