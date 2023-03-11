from unittest.mock import patch

from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.material.serializers import LiveSerializer
from apps.material.views import LiveViewSet
from utils.auth import BearerTokenAuthentication
from utils.mixins.service_context import ListObjectServiceContextMixin


class TestLiveViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = LiveViewSet()

    def test_parent_class(self):
        assert issubclass(LiveViewSet, ListObjectServiceContextMixin)
        assert issubclass(LiveViewSet, GenericViewSet)
        assert issubclass(LiveViewSet, ListModelMixin)

    def test_authentication_classes(self):
        assert self.view.authentication_classes == [BearerTokenAuthentication]

    def test_permission_classes(self):
        assert self.view.permission_classes == [IsAuthenticated]

    def test_serializer_class(self):
        assert self.view.serializer_class == LiveSerializer

    @patch("apps.material.views.lives.super")
    def test_list(self, mock_super):
        result = self.view.list({}, [], {})

        mock_super.return_value.list.asset_called_once_with({}, [], {})
        assert result == mock_super.return_value.list.return_value
