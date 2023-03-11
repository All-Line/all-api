from rest_framework.permissions import BasePermission


class UserPermissions(BasePermission):
    protected_methods = ("GET", "PATCH", "PUT", "DELETE")

    def has_permission(self, request, _):
        user = request.user
        method = request.method
        is_authenticated = user.is_authenticated

        is_confirming_the_email = "confirm_email" in request._request.path

        if is_confirming_the_email:
            return True

        if method in self.protected_methods and not is_authenticated:
            return False

        return True
