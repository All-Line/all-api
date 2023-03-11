from unittest.mock import patch

from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from apps.buying.serializers import CreateContractSerializer, PackageSerializer
from apps.buying.views import ContractViewSet, PackageViewSet
from utils.auth import BearerTokenAuthentication
from utils.mixins.service_context import ReadWithServiceContextMixin


class TestPackageViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = PackageViewSet

    def test_parent_class(self):
        assert issubclass(PackageViewSet, ReadWithServiceContextMixin)
        assert issubclass(PackageViewSet, ReadOnlyModelViewSet)

    def test_authentication_classes(self):
        assert self.view.authentication_classes == [BearerTokenAuthentication]

    def test_permission_classes(self):
        assert self.view.permission_classes == [IsAuthenticated]

    def test_serializer_class(self):
        assert self.view.serializer_class == PackageSerializer

    def test_lookup_field(self):
        assert self.view.lookup_field == "slug"

    @patch("apps.buying.views.super")
    def test_retrieve(self, mock_super):
        result = self.view.retrieve({}, [], {})

        mock_super.return_value.retrieve.asset_called_once_with({}, [], {})
        assert result == mock_super.return_value.retrieve.return_value

    @patch("apps.buying.views.super")
    def test_list(self, mock_super):
        result = self.view.list({}, [], {})

        mock_super.return_value.retrieve.asset_called_once_with({}, [], {})
        assert result == mock_super.return_value.list.return_value


class TestContractViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = ContractViewSet

    def test_parent_class(self):
        assert issubclass(ContractViewSet, GenericViewSet)
        assert issubclass(ContractViewSet, CreateModelMixin)

    def test_authentication_classes(self):
        assert self.view.authentication_classes == [BearerTokenAuthentication]

    def test_permission_classes(self):
        assert self.view.permission_classes == [IsAuthenticated]

    def test_serializer_class(self):
        assert self.view.serializer_class == CreateContractSerializer

    @patch("apps.buying.views.super")
    def test_create(self, mock_super):
        result = self.view().create({}, [], {})

        mock_super.return_value.create.assert_called_once_with({}, [], {})
        assert result == mock_super.return_value.create.return_value
