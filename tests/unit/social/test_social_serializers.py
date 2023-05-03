from unittest.mock import Mock, patch

import pytest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.social.models import (
    PostCommentModel,
    PostModel,
    ReactionModel,
    ReactionTypeModel,
)
from apps.social.serializers import (
    CreatePostCommentSerializer,
    CreateReactionSerializer,
    ListPostCommentSerializer,
    ListPostSerializer,
    ListReactionSerializer,
    ListReactTypesSerializer,
    UnreactSerializer,
)


class TestListReactionSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = ListReactionSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == ReactionModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == "__all__"

    def test_meta_depth(self):
        assert self.serializer.Meta.depth == 1


class TestListPostSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = ListPostSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == PostModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == "__all__"

    def test_meta_depth(self):
        assert self.serializer.Meta.depth == 1

    @patch("apps.social.serializers.ListPostCommentSerializer")
    def test_get_comments(self, mock_list_post_comment_serializer):
        obj = Mock()

        result = self.serializer().get_comments(obj)

        obj.comments.all.assert_called_once_with()
        mock_list_post_comment_serializer.assert_called_once_with(
            obj.comments.all.return_value, many=True
        )

        assert result == mock_list_post_comment_serializer.return_value.data


class TestCreatePostCommentSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = CreatePostCommentSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.Serializer)

    def test_content_field(self):
        assert "content" in self.serializer().fields

    def test_post_field(self):
        assert "post" in self.serializer().fields

    def test_answer_field(self):
        assert "answer" in self.serializer().fields

    @patch("apps.social.serializers.PostCommentModel.objects.create")
    def test_create(self, mock_post_comment_model_objects_create):
        request = Mock()
        request.user = Mock()
        validated_data = {}

        result = self.serializer(context={"request": request}).create(validated_data)

        mock_post_comment_model_objects_create.assert_called_once_with(
            author=request.user,
            **validated_data,
        )

        assert result == mock_post_comment_model_objects_create.return_value


class TestListPostCommentSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = ListPostCommentSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == PostCommentModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "content",
            "author",
            "answers",
            "reactions",
            "attachment",
        ]


class TestCreateReactionSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = CreateReactionSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.Serializer)

    def test_reaction_type_field(self):
        assert "reaction_type" in self.serializer().fields

    def test_create(self):
        validated_data = {"reaction_type": Mock(), "post": Mock()}
        request = Mock()
        serializer = self.serializer(context={"request": request})

        result = serializer.create(validated_data)

        validated_data["post"].react.assert_called_once_with(
            user=request.user,
            reaction_type_id=validated_data["reaction_type"].id,
        )

        assert result == validated_data["post"].react.return_value


class TestListReactTypesSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = ListReactTypesSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == ReactionTypeModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == "__all__"


class TestUnreactSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = UnreactSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.Serializer)

    def test_create(self):
        user = Mock()
        validated_data = {"reaction": Mock(user=user)}
        request = Mock(user=user)
        serializer = self.serializer(context={"request": request})

        result = serializer.create(validated_data)

        validated_data["reaction"].delete.assert_called_once()

        assert result == validated_data["reaction"].delete.return_value

    def test_create_with_validation_error(self):
        user = Mock()
        validated_data = {"reaction": Mock(user=user)}
        request = Mock(user=None)
        serializer = self.serializer(context={"request": request})

        with pytest.raises(ValidationError):
            serializer.create(validated_data)

        validated_data["reaction"].delete.assert_not_called()
