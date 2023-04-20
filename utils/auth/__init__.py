from rest_framework.authentication import (  # pragma: nocover
    TokenAuthentication,
)


class BearerTokenAuthentication(TokenAuthentication):  # pragma: nocover
    keyword = "Bearer"
