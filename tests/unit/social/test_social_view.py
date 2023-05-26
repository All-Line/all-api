from unittest.mock import Mock, patch

import pytest
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.social.models import PostCommentModel
from apps.social.serializers import (
    AnswerLoginQuestionSerializer,
    CompleteMissionSerializer,
    CreatePostCommentSerializer,
    CreateReactionSerializer,
    ListMissionSerializer,
    ListPostSerializer,
    ListReactTypesSerializer,
    LoginQuestionSerializer,
    UnreactSerializer,
    UpdatePostCommentSerializer,
)
from apps.social.views import (
    LoginQuestionViewSet,
    MissionViewSet,
    PostViewSet,
    ServiceAndEventContextMixin,
)
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
        assert PostViewSet.permission_classes == [IsAuthenticated]

    def test_serializers(self):
        assert PostViewSet.serializers == {
            "list": ListPostSerializer,
            "retrieve": ListPostSerializer,
            "comment": CreatePostCommentSerializer,
            "react": CreateReactionSerializer,
            "unreact": UnreactSerializer,
            "react_types": ListReactTypesSerializer,
            "update_comment": UpdatePostCommentSerializer,
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

    @patch("apps.social.views.get_object_or_404")
    @patch("apps.social.views.Response")
    @patch("apps.social.views.ListPostCommentSerializer")
    @patch.object(PostViewSet, "get_serializer")
    def test_update_comment_with_patch_method(
        self,
        mock_get_serializers,
        mock_list_post_comment_serializer,
        mock_response,
        mock_get_object_or_404,
    ):
        view = self.view
        request = Mock(method="PATCH")
        view.request = request
        result = self.view.update_comment(request, "some_comment_id")

        mock_get_object_or_404.assert_called_once_with(
            PostCommentModel,
            id="some_comment_id",
            author=request.user,
            is_deleted=False,
        )
        mock_instance = mock_get_object_or_404.return_value
        mock_get_serializers.assert_called_once_with(
            mock_instance, data=request.data, partial=True
        )
        mock_serializer = mock_get_serializers.return_value
        mock_serializer.is_valid.assert_called_once_with(raise_exception=True)
        mock_serializer.save.assert_called_once()

        mock_list_post_comment_serializer.assert_called_once_with(
            mock_serializer.save.return_value
        )
        mock_response.assert_called_once_with(
            mock_list_post_comment_serializer.return_value.data
        )

        mock_instance.delete.assert_not_called()

        assert result == mock_response.return_value

    @patch("apps.social.views.get_object_or_404")
    @patch("apps.social.views.Response")
    @patch("apps.social.views.ListPostCommentSerializer")
    @patch.object(PostViewSet, "get_serializer")
    def test_update_comment_with_delete_method(
        self,
        mock_get_serializers,
        mock_list_post_comment_serializer,
        mock_response,
        mock_get_object_or_404,
    ):
        view = self.view
        request = Mock(method="DELETE")
        view.request = request
        result = self.view.update_comment(request, "some_comment_id")

        mock_get_object_or_404.assert_called_once_with(
            PostCommentModel,
            id="some_comment_id",
            author=request.user,
            is_deleted=False,
        )
        mock_instance = mock_get_object_or_404.return_value
        mock_instance.delete.assert_called_once()

        mock_get_serializers.assert_not_called()
        mock_serializer = mock_get_serializers.return_value
        mock_serializer.is_valid.assert_not_called()
        mock_serializer.save.assert_not_called()

        mock_list_post_comment_serializer.assert_not_called()

        mock_response.assert_called_once_with(status=204)

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


class TestMissionViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = MissionViewSet()

    def test_parent_class(self):
        assert issubclass(MissionViewSet, ServiceAndEventContextMixin)
        assert issubclass(MissionViewSet, MultiSerializerMixin)
        assert issubclass(MissionViewSet, GenericViewSet)
        assert issubclass(MissionViewSet, mixins.RetrieveModelMixin)
        assert issubclass(MissionViewSet, mixins.ListModelMixin)

    def test_authentication_classes(self):
        assert MissionViewSet.authentication_classes == [BearerTokenAuthentication]

    def test_permission_classes(self):
        assert MissionViewSet.permission_classes == [IsAuthenticated]

    def test_serializers(self):
        assert MissionViewSet.serializers == {
            "list": ListMissionSerializer,
            "retrieve": ListMissionSerializer,
            "complete": CompleteMissionSerializer,
        }

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

    @patch("apps.social.views.Response")
    @patch.object(MissionViewSet, "get_serializer")
    def test_complete(self, mock_get_serializer, mock_response):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.complete(request)

        mock_get_serializer.assert_called_once_with(data=request.data)
        mock_serializer = mock_get_serializer.return_value
        mock_serializer.is_valid.assert_called_once_with(raise_exception=True)
        mock_serializer.save.assert_called_once()
        mock_response.assert_called_once_with(status=204)

        assert result == mock_response.return_value


class TestLoginQuestionViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = LoginQuestionViewSet()

    def test_parent_class(self):
        assert issubclass(LoginQuestionViewSet, MultiSerializerMixin)
        assert issubclass(LoginQuestionViewSet, GenericViewSet)
        assert issubclass(LoginQuestionViewSet, mixins.RetrieveModelMixin)
        assert issubclass(LoginQuestionViewSet, mixins.ListModelMixin)

    def test_authentication_classes(self):
        assert LoginQuestionViewSet.authentication_classes == [
            BearerTokenAuthentication
        ]

    def test_permission_classes(self):
        assert LoginQuestionViewSet.permission_classes == [IsAuthenticated]

    def test_serializers(self):
        assert LoginQuestionViewSet.serializers == {
            "list": LoginQuestionSerializer,
            "retrieve": LoginQuestionSerializer,
            "answer": AnswerLoginQuestionSerializer,
        }

    @patch("apps.social.views.super")
    def test_get_queryset_successfully(self, mock_super):
        view = self.view
        request = Mock()
        view.request = request
        result = view.get_queryset()

        mock_super.assert_called_once()
        mock_super.return_value.get_queryset.assert_called_once()

        mock_queryset = mock_super.return_value.get_queryset.return_value

        mock_queryset.filter.assert_called_once_with(event_id=request.user.event_id)

        mock_filtered_queryset = mock_queryset.filter.return_value

        mock_filtered_queryset.exclude.assert_called_once_with(
            answers__user_id=request.user.id
        )

        assert result == mock_filtered_queryset.exclude.return_value

    @patch("apps.social.views.super")
    def test_get_queryset_failure(self, mock_super):
        view = self.view
        request = Mock(user=Mock(is_guest=False))
        view.request = request

        with pytest.raises(ValidationError):
            view.get_queryset()

        mock_super.assert_called_once()
        mock_super.return_value.get_queryset.assert_called_once()

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

    @patch("apps.social.views.Response")
    @patch.object(LoginQuestionViewSet, "get_serializer")
    def test_answer(self, mock_get_serializer, mock_response):
        view = self.view
        request = Mock()
        view.request = request
        result = self.view.answer(request)

        mock_get_serializer.assert_called_once_with(data=request.data)
        mock_serializer = mock_get_serializer.return_value
        mock_serializer.is_valid.assert_called_once_with(raise_exception=True)
        mock_serializer.save.assert_called_once()
        mock_response.assert_called_once_with(status=204)

        assert result == mock_response.return_value
