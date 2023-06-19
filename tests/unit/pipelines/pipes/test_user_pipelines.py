from unittest.mock import Mock

from pipelines.base import BasePipeline
from pipelines.items import CreateUser, GenerateRandomUsername, GenerateToken, SendEmail
from pipelines.items.add_mention_on_comment import AddMentionOnComment
from pipelines.pipes import CreateUserPipeline
from pipelines.pipes.user import MentionGuestPipeline, NotifyGuestNewPostPipeline


class TestCreateUserPipeline:
    @classmethod
    def setup_class(cls):
        cls.pipeline = CreateUserPipeline
        cls.base_pipeline_data = {
            "first_name": "some_first_name",
            "last_name": "some_last_name",
            "email": "some_email",
            "password": "some_password",
            "service": "some_service",
            "birth_date": "some_birth_date",
        }

    def test_parent_class(self):
        assert issubclass(self.pipeline, BasePipeline)

    def test_init(self):
        user_create_pipeline = self.pipeline(**self.base_pipeline_data)

        assert user_create_pipeline.first_name == "some_first_name"
        assert user_create_pipeline.last_name == "some_last_name"
        assert user_create_pipeline.email == "some_email"
        assert user_create_pipeline.password == "some_password"
        assert user_create_pipeline.service == "some_service"
        assert user_create_pipeline.kwargs == {
            "birth_date": "some_birth_date",
        }

    def test_pipelines_items(self):
        user_create_pipeline = self.pipeline(**self.base_pipeline_data)

        steps = user_create_pipeline.steps
        assert steps == [
            GenerateRandomUsername,
            CreateUser,
            GenerateToken,
            SendEmail,
        ]


class TestMentionGuestPipeline:
    @classmethod
    def setup_class(cls):
        cls.pipeline = MentionGuestPipeline

    def test_parent_class(self):
        assert issubclass(self.pipeline, BasePipeline)

    def test_init(self):
        mock_user = Mock()
        mock_comment = Mock()
        mention_guest_pipeline = self.pipeline(
            user=mock_user,
            comment=mock_comment,
        )

        assert mention_guest_pipeline.user == mock_user
        assert mention_guest_pipeline.comment == mock_comment
        assert mention_guest_pipeline.email_type == "mention_notification"
        assert mention_guest_pipeline.send_mail is True

    def test_pipelines_items(self):
        mock_user = Mock()
        mock_comment = Mock()
        mention_guest_pipeline = self.pipeline(
            user=mock_user,
            comment=mock_comment,
        )

        steps = mention_guest_pipeline.steps
        assert steps == [
            AddMentionOnComment,
            SendEmail,
        ]


class TestNotifyGuestNewPostPipeline:
    @classmethod
    def setup_class(cls):
        cls.pipeline = NotifyGuestNewPostPipeline

    def test_parent_class(self):
        assert issubclass(self.pipeline, BasePipeline)

    def test_init(self):
        mock_user = Mock()
        mention_guest_pipeline = self.pipeline(
            user=mock_user,
        )

        assert mention_guest_pipeline.user == mock_user
        assert mention_guest_pipeline.email_type == "new_post_notification"
        assert mention_guest_pipeline.send_mail is True

    def test_pipelines_items(self):
        mock_user = Mock()
        mention_guest_pipeline = self.pipeline(
            user=mock_user,
        )

        steps = mention_guest_pipeline.steps
        assert steps == [
            SendEmail,
        ]
