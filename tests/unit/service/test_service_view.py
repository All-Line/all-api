from unittest.mock import Mock, patch

import pytest
from django.http import Http404
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.service.serializers import (
    RetrieveServiceSerializer,
    ServiceCredentialConfigSerializer,
    TermsServiceSerializer,
)
from apps.service.views import ServiceViewSet
from utils.mixins.multiserializer import MultiSerializerMixin


class TestServiceViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = ServiceViewSet()

    def test_parent_class(self):
        assert issubclass(ServiceViewSet, MultiSerializerMixin)
        assert issubclass(ServiceViewSet, mixins.RetrieveModelMixin)
        assert issubclass(ServiceViewSet, GenericViewSet)

    def test_serializers(self):
        assert self.view.serializers == {
            "retrieve": RetrieveServiceSerializer,
            "terms": TermsServiceSerializer,
            "credential_fields": ServiceCredentialConfigSerializer,
        }

    def test_lookup_field(self):
        assert self.view.lookup_field == "slug"

    @patch("apps.service.views.super")
    def test_retrieve(self, mock_super):
        request = Mock()
        result = self.view.retrieve(request)

        mock_super.assert_called_once()
        mock_super.return_value.retrieve.assert_called_once_with(request)

        assert result == mock_super.return_value.retrieve.return_value

    @patch("apps.service.views.Response")
    @patch("apps.service.views.ServiceViewSet.get_object")
    def test_terms(self, mock_get_object, mock_response):
        result = self.view.terms(None, "bar")

        mock_get_object.assert_called_once()
        mock_response.assert_called_once_with(
            {"terms": mock_get_object.return_value.terms}
        )
        assert result == mock_response.return_value

    @patch("apps.service.views.Response")
    @patch("apps.service.views.ServiceViewSet.get_object")
    @patch("apps.service.views.ServiceViewSet.get_serializer")
    def test_credential_fields_with_valid_credential_config_type(
        self, mock_get_serializer, mock_get_object, mock_response
    ):
        result = self.view.credential_fields(None, "register")

        service = mock_get_object.return_value
        mock_get_object.assert_called_once()
        service.credential_configs.only.assert_called_once_with(
            "id",
            "credential_config_type",
            "field",
            "label",
            "field_html_type",
            "rule",
            "no_match_message",
        )
        service.credential_configs.only.return_value.filter.assert_called_once_with(
            credential_config_type="register", is_active=True
        )

        mock_get_serializer.assert_called_once_with(
            service.credential_configs.only.return_value.filter.return_value, many=True
        )
        mock_response.assert_called_once_with(mock_get_serializer.return_value.data)
        assert result == mock_response.return_value

    @patch("apps.service.views.Response")
    @patch("apps.service.views.ServiceViewSet.get_object")
    @patch("apps.service.views.ServiceViewSet.get_serializer")
    def test_credential_fields_with_invalid_credential_config_type(
        self, mock_get_serializer, mock_get_object, mock_response
    ):
        with pytest.raises(Http404):
            self.view.credential_fields(None, "foo")

        service = mock_get_object.return_value
        mock_get_object.assert_not_called()
        service.credential_configs.filter.assert_not_called()

        mock_get_serializer.assert_not_called()
        mock_response.assert_not_called()
