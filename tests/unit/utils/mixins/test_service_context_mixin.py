from unittest.mock import Mock, patch

import pytest
from django.http import Http404

from apps.material.views import LiveViewSet
from utils.mixins.service_context import (
    ListObjectServiceContextMixin,
    ReadWithServiceContextMixin,
    RetrieveObjectServiceContextMixin,
)


class TestListObjectServiceContextMixin:
    @patch("utils.mixins.service_context.super")
    def test_filter_queryset(self, mock_super):
        mock_self = Mock()
        result = LiveViewSet.filter_queryset(mock_self, {})

        queryset = mock_super.return_value.filter_queryset.return_value
        mock_super.return_value.filter_queryset.asset_called_once_with({})
        queryset.filter.assert_called_once_with(service=mock_self.request.user.service)
        assert result == queryset.filter.return_value


class TestRetrieveObjectServiceContextMixin:
    @patch("utils.mixins.service_context.super")
    def test_get_object_with_different_service(self, mock_super):
        mock_self = Mock()

        with pytest.raises(Http404):
            ReadWithServiceContextMixin.get_object(mock_self)

        mock_super.return_value.get_object.assert_called_once()

    @patch("utils.mixins.service_context.super")
    def test_get_object(self, mock_super):
        service_id = 1
        mock_super.return_value.get_object.return_value.service_id = service_id
        mock_self = Mock()
        mock_self.request.user.service_id = service_id
        result = ReadWithServiceContextMixin.get_object(mock_self)

        mock_super.return_value.get_object.assert_called_once()
        assert result == mock_super.return_value.get_object.return_value


class TestReadWithServiceContextMixin:
    def test_parent_class(self):
        assert issubclass(
            ReadWithServiceContextMixin, RetrieveObjectServiceContextMixin
        )
        assert issubclass(ReadWithServiceContextMixin, ListObjectServiceContextMixin)
