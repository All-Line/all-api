from unittest.mock import Mock, patch

import pytest
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.material.serializers import CourseSerializer
from apps.material.views import CourseViewSet
from utils.auth import BearerTokenAuthentication
from utils.exceptions.http import HttpPaymentRequired
from utils.mixins.service_context import ReadWithServiceContextMixin


class TestCourseViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = CourseViewSet()

    def test_parent_class(self):
        assert issubclass(CourseViewSet, ReadWithServiceContextMixin)
        assert issubclass(CourseViewSet, ReadOnlyModelViewSet)

    def test_authentication_classes(self):
        assert self.view.authentication_classes == [BearerTokenAuthentication]

    def test_permission_classes(self):
        assert self.view.permission_classes == [IsAuthenticated]

    def test_serializer_class(self):
        assert self.view.serializer_class == CourseSerializer

    def test_lookup_field(self):
        assert self.view.lookup_field == "slug"

    @patch("apps.material.views.courses.super")
    def test_retrieve(self, mock_super):
        result = self.view.retrieve({}, [], {})

        mock_super.return_value.retrieve.asset_called_once_with({}, [], {})
        assert result == mock_super.return_value.retrieve.return_value

    @patch("apps.material.views.courses.super")
    def test_list(self, mock_super):
        result = self.view.list({}, [], {})

        mock_super.return_value.retrieve.asset_called_once_with({}, [], {})
        assert result == mock_super.return_value.list.return_value

    @patch("apps.material.views.courses.super")
    def test_get_object_failure_due_to_user_dont_have_access(self, mock_super):
        mock_self = Mock()
        mock_self.request.user.can_access.return_value = False

        with pytest.raises(HttpPaymentRequired):
            CourseViewSet.get_object(mock_self)

        mock_super.return_value.get_object.assert_called_once()
        mock_self.request.user.can_access.assert_called_once_with(
            mock_super.return_value.get_object.return_value
        )

    @patch("apps.material.views.courses.super")
    def test_get_object_successfully(self, mock_super):
        mock_self = Mock()
        result = CourseViewSet.get_object(mock_self)

        mock_super.return_value.get_object.assert_called_once()
        assert result == mock_super.return_value.get_object.return_value
