from unittest.mock import Mock, patch

import pytest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.social.models import (
    LoginQuestionOption,
    LoginQuestions,
    MissionModel,
    MissionTypeModel,
    PostCommentModel,
    PostModel,
    ReactionModel,
    ReactionTypeModel,
)
from apps.social.serializers import (
    AnswerLoginQuestionSerializer,
    CompleteMissionSerializer,
    CreatePostCommentSerializer,
    CreateReactionSerializer,
    ListAllPostSerializer,
    ListMissionSerializer,
    ListPostCommentSerializer,
    ListPostSerializer,
    ListReactionSerializer,
    ListReactTypesSerializer,
    LoginQuestionOptionSerializer,
    LoginQuestionSerializer,
    MissionTypeSerializer,
    UnreactSerializer,
    UpdatePostCommentSerializer,
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
        assert self.serializer.Meta.fields == [
            "id",
            "author",
            "event",
            "reactions",
            "comments",
            "date_joined",
            "attachment",
            "attachment_type",
            "my_reaction",
            "description",
        ]

    def test_meta_depth(self):
        assert self.serializer.Meta.depth == 1

    @patch("apps.social.serializers.ListPostCommentSerializer")
    def test_get_comments(self, mock_list_post_comment_serializer):
        obj = Mock()

        result = self.serializer().get_comments(obj)

        obj.comments.filter.assert_called_once_with(is_deleted=False)
        mock_list_post_comment_serializer.assert_called_once_with(
            obj.comments.filter.return_value.order_by.return_value,
            many=True,
            context={},
        )

        assert result == mock_list_post_comment_serializer.return_value.data

    def test_get_attachment_type(self):
        obj = Mock()
        result = self.serializer().get_attachment_type(obj)
        assert result == obj.attachment_type

    @patch("apps.social.serializers.ListReactionSerializer")
    def test_get_my_reaction(self, mock_list_reaction_serializer):
        mock_obj = Mock()
        mock_request = Mock()
        serializer = self.serializer(context={"request": mock_request})

        result = serializer.get_my_reaction(mock_obj)

        mock_obj.get_reaction_by_user.assert_called_once_with(mock_request.user)
        mock_list_reaction_serializer.assert_called_once_with(
            mock_obj.get_reaction_by_user.return_value
        )
        assert result == mock_list_reaction_serializer.return_value.data


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
    @patch("apps.social.serializers.MentionGuestPipeline")
    def test_create(
        self, mock_mention_guest_pipeline, mock_post_comment_model_objects_create
    ):
        request = Mock()
        request.user = Mock()
        mock_mentions = [Mock()]
        validated_data = {"mentions": mock_mentions}

        result = self.serializer(context={"request": request}).create(validated_data)

        mock_mention_guest_pipeline.assert_called_once_with(
            mock_mentions[0],
            mock_post_comment_model_objects_create.return_value,
        )

        mock_mention_guest_pipeline.return_value.run.assert_called_once()

        mock_post_comment_model_objects_create.assert_called_once_with(
            author=request.user,
            **validated_data,
        )

        assert result == mock_post_comment_model_objects_create.return_value


class TestListAllPostSerializer:
    def test_get_comments(self):
        mock_obj = Mock()
        result = ListAllPostSerializer.get_comments(Mock(), mock_obj)

        mock_obj.comments.filter.assert_called_once_with(is_deleted=False)
        mock_obj.comments.filter.return_value.count.assert_called_once()

        assert result == {
            "length": mock_obj.comments.filter.return_value.count.return_value,
        }


class TestUpdatePostCommentSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = UpdatePostCommentSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.Serializer)

    def test_content_field(self):
        assert "content" in self.serializer().fields

    def test_attachment_field(self):
        assert "attachment" in self.serializer().fields

    def test_update(self):
        mock_instance = Mock()
        mock_validated_data = {
            "content": Mock(),
            "attachment": Mock(),
        }

        serializer = self.serializer()
        result = serializer.update(mock_instance, mock_validated_data)

        mock_instance.save.assert_called_once()

        assert mock_instance.content == mock_validated_data["content"]
        assert mock_instance.attachment == mock_validated_data["attachment"]
        assert result == mock_instance


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
            "my_reaction",
            "attachment",
            "attachment_type",
            "mentions",
            "date_joined",
        ]

    @patch("apps.social.serializers.ListPostCommentSerializer")
    def test_get_answers(self, mock_list_post_comment_serializer):
        mock_obj = Mock()
        serializer = self.serializer()

        result = serializer.get_answers(mock_obj)

        mock_obj.answers.all.assert_called_once()
        mock_list_post_comment_serializer.assert_called_once_with(
            mock_obj.answers.all.return_value, many=True, context={}
        )

        assert result == mock_list_post_comment_serializer.return_value.data

    @patch("apps.social.serializers.ListReactionSerializer")
    def test_get_my_reaction(self, mock_list_reaction_serializer):
        mock_obj = Mock()
        mock_request = Mock()
        serializer = self.serializer(context={"request": mock_request})

        result = serializer.get_my_reaction(mock_obj)

        mock_obj.get_reaction_by_user.assert_called_once_with(mock_request.user)
        mock_list_reaction_serializer.assert_called_once_with(
            mock_obj.get_reaction_by_user.return_value
        )
        assert result == mock_list_reaction_serializer.return_value.data


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


class TestMissionTypeSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = MissionTypeSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == MissionTypeModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == ["name"]


class TestListMissionSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = ListMissionSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == MissionModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "type",
            "title",
            "description",
            "attachment",
            "attachment_type",
            "thumbnail",
            "is_completed",
            "completed_info",
        ]

    def test_meta_depth(self):
        assert self.serializer.Meta.depth == 1

    def test_get_completed_info(self):
        mock_obj = Mock()
        mock_request = Mock()
        serializer = self.serializer(context={"request": mock_request})

        result = serializer.get_completed_info(mock_obj)

        mock_obj.get_completed_info.assert_called_once_with(mock_request.user)

        mock_completed_info = mock_obj.get_completed_info.return_value
        assert result == {
            "content": mock_completed_info.content,
            "attachment": mock_completed_info.attachment.url,
            "attachment_type": mock_completed_info.attachment_type,
        }

    def test_get_is_completed(self):
        mock_obj = Mock()
        mock_request = Mock()
        serializer = self.serializer(context={"request": mock_request})

        result = serializer.get_is_completed(mock_obj)

        mock_obj.is_completed.assert_called_once_with(mock_request.user)

        assert result == mock_obj.is_completed.return_value


class TestCompleteMissionSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = CompleteMissionSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.Serializer)

    def test_create_successfully(self):
        mock_validated_data = {
            "mission": Mock(is_completed=Mock(return_value=False)),
            "content": Mock(),
            "attachment": Mock(),
        }

        mock_request = Mock()
        serializer = self.serializer(context={"request": mock_request})

        result = serializer.create(mock_validated_data)

        mock_mission = mock_validated_data["mission"]

        mock_mission.is_completed.assert_called_once_with(mock_request.user)
        mock_mission.complete.assert_called_once_with(
            mock_request.user,
            mock_validated_data["attachment"],
            mock_validated_data["content"],
        )

        assert result == mock_mission.complete.return_value

    def test_create_with_validation_error(self):
        mock_validated_data = {
            "mission": Mock(is_completed=Mock(return_value=True)),
            "content": Mock(),
            "attachment": Mock(),
        }

        mock_request = Mock()
        serializer = self.serializer(context={"request": mock_request})

        with pytest.raises(ValidationError):
            serializer.create(mock_validated_data)

        mock_mission = mock_validated_data["mission"]

        mock_mission.is_completed.assert_called_once_with(mock_request.user)
        mock_mission.complete.assert_not_called()


class TestLoginQuestionOptionSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = LoginQuestionOptionSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == LoginQuestionOption

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == ["id", "option"]


class TestLoginQuestionSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = LoginQuestionSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == LoginQuestions

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == ["id", "question", "options"]


class TestAnswerLoginQuestionSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = AnswerLoginQuestionSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.Serializer)

    def test_create_successfully(self):
        mock_validated_data = {
            "question": Mock(is_answered=Mock(return_value=False)),
            "option": Mock(),
        }

        mock_request = Mock()
        serializer = self.serializer(context={"request": mock_request})

        result = serializer.create(mock_validated_data)

        mock_question = mock_validated_data["question"]
        mock_option = mock_validated_data["option"]

        mock_question.is_answered.assert_called_once_with(mock_request.user)
        mock_question.answer.assert_called_once_with(mock_request.user, mock_option)

        assert result == mock_question.answer.return_value

    def test_create_with_validation_error(self):
        mock_validated_data = {
            "question": Mock(is_answered=Mock(return_value=True)),
            "option": Mock(),
        }

        mock_request = Mock()
        serializer = self.serializer(context={"request": mock_request})

        with pytest.raises(ValidationError):
            serializer.create(mock_validated_data)

        mock_question = mock_validated_data["question"]

        mock_question.is_answered.assert_called_once_with(mock_request.user)
        mock_question.answer.assert_not_called()
