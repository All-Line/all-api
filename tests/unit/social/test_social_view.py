from unittest.mock import Mock, patch

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.social.permissions import PostPermissions
from apps.social.serializers import (
    CreatePostCommentSerializer,
    CreateReactionSerializer,
    ListPostSerializer,
    ListReactTypesSerializer,
    UnreactSerializer,
)
from apps.social.views import PostViewSet
from utils.auth import BearerTokenAuthentication
from utils.mixins.multiserializer import MultiSerializerMixin


class TestPostViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = PostViewSet()

    def test_parent_class(self):
        assert issubclass(PostViewSet, MultiSerializerMixin)
        assert issubclass(PostViewSet, mixins.RetrieveModelMixin)
        assert issubclass(PostViewSet, mixins.ListModelMixin)
        assert issubclass(PostViewSet, GenericViewSet)

    def test_authentication_classes(self):
        assert PostViewSet.authentication_classes == [BearerTokenAuthentication]

    def test_permission_classes(self):
        assert PostViewSet.permission_classes == [PostPermissions]

    def test_serializers(self):
        assert PostViewSet.serializers == {
            "list": ListPostSerializer,
            "retrieve": ListPostSerializer,
            "comment": CreatePostCommentSerializer,
            "react": CreateReactionSerializer,
            "unreact": UnreactSerializer,
            "react_types": ListReactTypesSerializer,
        }

    @patch("apps.social.views.super")
    def test_get_queryset(self, mock_super):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.get_queryset()

        mock_super.assert_called_once()
        mock_super.return_value.get_queryset.assert_called_once_with()

        queryset = mock_super.return_value.get_queryset.return_value

        queryset.filter.assert_called_once_with(
            service_id=request.user.service_id,
            event_id=request.user.event_id,
        )

        assert result == queryset.filter.return_value

    @patch("apps.social.views.super")
    def test_list(self, mock_super):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.list(request)

        mock_super.assert_called_once()
        mock_super.return_value.list.assert_called_once_with(request)

        assert result == mock_super.return_value.list.return_value

    @patch("apps.social.views.super")
    def test_retrieve(self, mock_super):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.retrieve(request)

        mock_super.assert_called_once()
        mock_super.return_value.retrieve.assert_called_once_with(request)

        assert result == mock_super.return_value.retrieve.return_value

    @patch.object(PostViewSet, "get_serializer")
    @patch("apps.social.views.ListPostCommentSerializer")
    @patch("apps.social.views.Response")
    def test_comment(self, mock_response, mock_serializer, mock_get_serializer):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.comment(request)

        mock_get_serializer.assert_called_once_with(data=request.data)
        mock_serializer.assert_called_once_with(
            mock_get_serializer.return_value.save.return_value
        )
        mock_response.assert_called_once_with(mock_serializer.return_value.data)

        assert result == mock_response.return_value

    @patch.object(PostViewSet, "get_serializer")
    @patch("apps.social.views.Response")
    def test_react(self, mock_response, mock_get_serializer):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.react(request)

        mock_get_serializer.assert_called_once_with(data=request.data)
        mock_response.assert_called_once_with(status=204)

        assert result == mock_response.return_value

    @patch.object(PostViewSet, "get_serializer")
    @patch("apps.social.views.Response")
    def test_unreact(self, mock_response, mock_get_serializer):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.unreact(request)

        mock_get_serializer.assert_called_once_with(data=request.data)
        mock_get_serializer.return_value.save.assert_called_once()
        mock_response.assert_called_once_with(status=204)

        assert result == mock_response.return_value

    @patch("apps.social.views.Response")
    @patch.object(PostViewSet, "get_serializer")
    @patch("apps.social.views.ReactionTypeModel")
    def test_react_types(
        self, mock_reaction_type_model, mock_get_serializer, mock_response
    ):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.react_types(request)

        mock_get_serializer.assert_called_once_with(
            mock_reaction_type_model.objects.filter.return_value, many=True
        )
        mock_response.assert_called_once_with(mock_get_serializer.return_value.data)

        assert result == mock_response.return_value
