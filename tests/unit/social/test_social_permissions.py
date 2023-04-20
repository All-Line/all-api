from unittest.mock import Mock

from apps.social.permissions import PostPermissions


class TestPostPermissions:
    def test_has_permission(self):
        permission = PostPermissions()
        request = Mock()

        result = permission.has_permission(request, None)

        user = request.user
        is_authenticated = user.is_authenticated

        assert result == is_authenticated
