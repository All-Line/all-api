from unittest.mock import Mock

from rest_framework.permissions import BasePermission

from apps.user.permissions import UserPermissions


class TestUserPermissions:
    @classmethod
    def setup_class(cls):
        cls.permission = UserPermissions

    def test_parent_class(self):
        assert issubclass(self.permission, BasePermission)

    def test_attr_protected_methods(self):
        assert self.permission.protected_methods == (
            "GET",
            "PATCH",
            "PUT",
            "DELETE",
        )

    def test_has_permission_successfully_with_path_has_confirm_email(self):
        mock_user = Mock(is_authenticated=False)
        mock_request = Mock(user=mock_user, method="GET")
        mock_request._request.path = "api/v1/user/confirm_email/"
        result = self.permission().has_permission(mock_request, None)

        assert result is True

    def test_has_permission_successfully(self):
        mock_user = Mock(is_authenticated=False)
        mock_request = Mock(user=mock_user, method="POST")
        mock_request._request.path = "api/v1/user/login/"
        result = self.permission().has_permission(mock_request, None)

        assert result is True

    def test_has_permission_failure(self):
        mock_user = Mock(is_authenticated=False)
        mock_request = Mock(user=mock_user, method="GET")
        mock_request._request.path = "api/v1/user/me/"
        result = self.permission().has_permission(mock_request, None)

        assert result is False
