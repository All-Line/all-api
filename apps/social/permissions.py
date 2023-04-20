from rest_framework.permissions import BasePermission


class PostPermissions(BasePermission):
    def has_permission(self, request, _):
        user = request.user
        is_authenticated = user.is_authenticated

        return is_authenticated
