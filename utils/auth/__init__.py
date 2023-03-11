from rest_framework.authentication import TokenAuthentication  # pragma: nocover


class BearerTokenAuthentication(TokenAuthentication):  # pragma: nocover
    keyword = "Bearer"
