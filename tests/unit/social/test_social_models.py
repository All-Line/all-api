from unittest.mock import Mock, call, patch

import pytest
from django.db import models

from apps.service.models import ServiceClientModel, ServiceModel
from apps.social.models import (
    AITextReportModel,
    EventModel,
    LoginAnswer,
    LoginQuestionOption,
    LoginQuestions,
    MissionInteractionModel,
    MissionModel,
    MissionTypeModel,
    PostCommentModel,
    PostModel,
    ReactionModel,
    ReactionsMixin,
    ReactionTypeModel,
    event_directory_path,
    mission_directory_path,
    mission_interaction_directory_path,
    post_attachment_directory_path,
)
from apps.user.models import UserModel
from utils.abstract_models.base_model import BaseModel


@patch("apps.social.models.datetime")
def test_post_attachment_directory_path(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = "01012020_12:00:00"
    instance = Mock()
    instance.author.first_name = "John"
    instance.id = 1
    filename = "test.jpg"

    result = post_attachment_directory_path(instance, filename)

    assert result == "media/posts/John_1_01012020_12:00:00_test.jpg"


@patch("apps.social.models.datetime")
def test_event_directory_path(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = "01012020_12:00:00"
    instance = Mock()
    instance.title = "Test"
    instance.id = 1
    filename = "test.jpg"

    result = event_directory_path(instance, filename)

    assert result == "media/event/Test_1_01012020_12:00:00_test.jpg"


@patch("apps.social.models.get_formatted_datetime_now")
def test_mission_interaction_directory_path(mock_get_formatted_datetime_now):
    mock_instance = Mock()
    mock_filename = "name"
    result = mission_interaction_directory_path(mock_instance, mock_filename)

    mock_get_formatted_datetime_now.assert_called_once()
    assert result == (
        f"media/mission_interaction/{mock_instance.user.id}"
        f"_{mock_instance.id}"
        f"_{mock_get_formatted_datetime_now.return_value}"
        f"_{mock_filename}"
    )


@patch("apps.social.models.get_formatted_datetime_now")
def test_mission_directory_path(mock_get_formatted_datetime_now):
    mock_instance = Mock()
    mock_filename = "name"
    result = mission_directory_path(mock_instance, mock_filename)

    mock_get_formatted_datetime_now.assert_called_once()
    assert result == (
        f"media/mission/{mock_instance.title}"
        f"_{mock_instance.id}"
        f"_{mock_get_formatted_datetime_now.return_value}"
        f"_{mock_filename}"
    )


class TestReactionsMixin:
    def test_reactions_amount(self):
        mixin = ReactionsMixin()
        mixin.reactions = Mock()

        result = mixin.reactions_amount

        mixin.reactions.count.assert_called_once()

        assert result == mixin.reactions.count.return_value

    def test_react_with_user_reaction(self):
        user = Mock()
        user_reaction = Mock()
        mixin = ReactionsMixin()
        mixin.reactions = Mock()
        mixin.reactions.filter.return_value.first.return_value = user_reaction

        result = mixin.react(user, 1)
        mixin.reactions.filter.assert_called_once_with(user=user)
        mixin.reactions.filter.return_value.first.assert_called_once()
        mixin.reactions.create.assert_not_called()

        user_reaction.save.assert_called_once()

        assert result == user_reaction
        assert user_reaction.reaction_type_id == 1

    def test_react_without_user_reaction(self):
        user = Mock()
        user_reaction = Mock()
        mixin = ReactionsMixin()
        mixin.reactions = Mock()
        mixin.reactions.filter.return_value.first.return_value = None
        mixin.reactions.create.return_value = user_reaction

        result = mixin.react(user, 1)
        mixin.reactions.filter.assert_called_once_with(user=user)
        mixin.reactions.filter.return_value.first.assert_called_once()
        mixin.reactions.create.assert_called_once_with(reaction_type_id=1, user=user)

        assert result == user_reaction


class TestReactionTypeModel:
    @classmethod
    def setup_class(cls):
        cls.model = ReactionTypeModel

    def test_str(self):
        reaction_type = ReactionTypeModel(name="some name")

        assert str(reaction_type) == "some name"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Reaction Type"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Reaction Types"

    def test_name_field(self):
        field = self.model._meta.get_field("name")

        assert type(field) == models.CharField
        assert field.verbose_name == "Name"
        assert field.max_length == 255

    def test_attachment_field(self):
        field = self.model._meta.get_field("attachment")

        assert type(field) == models.FileField
        assert field.verbose_name == "Attachment"
        assert field.upload_to.__name__ == "post_attachment_directory_path"
        assert field.null is True
        assert field.blank is True

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model is ServiceModel
        assert field.verbose_name == "Service"
        assert field.remote_field.related_name == "reaction_types"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 7


class TestReactionModel:
    @classmethod
    def setup_class(cls):
        cls.model = ReactionModel

    def test_str(self):
        reaction = ReactionModel(reaction_type=ReactionTypeModel(name="like"))

        assert str(reaction) == "like"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Reaction"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Reactions"

    def test_reaction_type_field(self):
        field = self.model._meta.get_field("reaction_type")

        assert type(field) == models.ForeignKey
        assert field.related_model is ReactionTypeModel
        assert field.verbose_name == "Reaction Type"
        assert field.remote_field.related_name == "reactions"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_user_field(self):
        field = self.model._meta.get_field("user")

        assert type(field) == models.ForeignKey
        assert field.related_model is UserModel
        assert field.verbose_name == "User"
        assert field.remote_field.related_name == "reactions"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 6


class TestPostCommentModel:
    @classmethod
    def setup_class(cls):
        cls.model = PostCommentModel

    def test_str(self):
        comment = PostCommentModel(author=UserModel(first_name="John"))

        assert str(comment) == "John's comment"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "User Comment"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "User Comments"

    def test_content_field(self):
        field = self.model._meta.get_field("content")

        assert type(field) == models.TextField
        assert field.verbose_name == "Content"
        assert field.null is True
        assert field.blank is True

    def test_post_field(self):
        field = self.model._meta.get_field("post")

        assert type(field) == models.ForeignKey
        assert field.related_model is PostModel
        assert field.verbose_name == "Post"
        assert field.remote_field.related_name == "comments"
        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.null is True
        assert field.blank is True

    def test_answer_field(self):
        field = self.model._meta.get_field("answer")

        assert type(field) == models.ForeignKey
        assert field.related_model is PostCommentModel
        assert field.verbose_name == "Answer"
        assert field.remote_field.related_name == "answers"
        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.null is True
        assert field.blank is True

    def test_reactions_field(self):
        field = self.model._meta.get_field("reactions")

        assert type(field) == models.ManyToManyField
        assert field.related_model is ReactionModel
        assert field.verbose_name == "Reactions"
        assert field.remote_field.related_name == "comments"
        assert field.blank is True

    def test_author_field(self):
        field = self.model._meta.get_field("author")

        assert type(field) == models.ForeignKey
        assert field.related_model is UserModel
        assert field.verbose_name == "Author"
        assert field.remote_field.related_name == "post_comments"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_is_answer(self):
        post_comment = PostCommentModel()

        assert post_comment.is_answer is False

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 9


class TestEventModel:
    @classmethod
    def setup_class(cls):
        cls.model = EventModel

    def test_str(self):
        event = EventModel(title="some title")

        assert str(event) == "some title"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Event"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Events"

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255

    def test_description_field(self):
        field = self.model._meta.get_field("description")

        assert type(field) == models.TextField
        assert field.verbose_name == "Description"
        assert field.null is True
        assert field.blank is True

    def test_attachment_field(self):
        field = self.model._meta.get_field("attachment")

        assert type(field) == models.FileField
        assert field.verbose_name == "Attachment"
        assert field.upload_to.__name__ == "event_directory_path"
        assert field.null is True
        assert field.blank is True

    def test_event_type_field(self):
        field = self.model._meta.get_field("event_type")

        assert type(field) == models.CharField
        assert field.verbose_name == "Event Type"
        assert field.max_length == 255
        assert field.choices == EventModel.EVENT_TYPE
        assert field.default == "closed"
        assert field.help_text == (
            'This property, when "Open", allows anyone to access the event. '
            'When "Closed", a certain group will only be able to access the '
            'event: fill in the "Guests" field in this case.'
        )

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model is ServiceModel
        assert field.verbose_name == "Service"
        assert field.remote_field.related_name == "events"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_guests_field(self):
        field = self.model._meta.get_field("guests")

        assert type(field) == models.TextField
        assert field.verbose_name == "Guests"
        assert field.null is True
        assert field.blank is True
        assert (
            field.help_text
            == """
            Enter guests in the following format:
            <br>
            name;email,name;email,name;email,name;email,...
            <br>
            Like:
            <br>
            John Doe;john@mail.com,Elisa Jax;elisa@mail.com,Edward,edward.us@mail.com,...
        """  # noqa: E501
        )

    def test_send_email_to_guests_field(self):
        field = self.model._meta.get_field("send_email_to_guests")

        assert type(field) == models.BooleanField
        assert field.verbose_name == "Send email to guests"
        assert field.default is False
        assert field.help_text == ("Send email to guests with their credentials")

    def test_event_link_field(self):
        field = self.model._meta.get_field("event_link")

        assert type(field) == models.URLField
        assert field.verbose_name == "Event Link"
        assert field.help_text == "Link for guests to access the event"
        assert field.null is True
        assert field.blank is True

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 15

    def test_get_guests(self):
        event = EventModel(guests="Some Name1;email1,Some Name2;email2")

        assert event.get_guests() == [
            "Some Name1;email1",
            "Some Name2;email2",
        ]

    def test_verify_errors(self):
        errors = []
        email = "wrong_email.com"

        self.model._verify_errors(errors, email)

        assert errors == [
            "Wrong email format: wrong_email.com",
        ]

    @pytest.mark.parametrize(
        "email, expected",
        [
            # Email fail cases
            (
                "andrew.com",
                ["Wrong email format: andrew.com"],
            ),
            (
                "andrew@.com",
                ["Wrong email format: andrew@.com"],
            ),
            (
                "andrew@gmail.c",
                ["Wrong email format: andrew@gmail.c"],
            ),
            (
                "andrew@com",
                ["Wrong email format: andrew@com"],
            ),
            (
                "andrew@com.",
                ["Wrong email format: andrew@com."],
            ),
            (
                "andrew@gmail",
                ["Wrong email format: andrew@gmail"],
            ),
            (
                "andrew@gmail.",
                ["Wrong email format: andrew@gmail."],
            ),
            (
                "andrew@gmail!",
                ["Wrong email format: andrew@gmail!"],
            ),
            (
                "andrew@$gmail.com",
                ["Wrong email format: andrew@$gmail.com"],
            ),
            (
                ".andrew@gmail.com",
                ["Wrong email format: .andrew@gmail.com"],
            ),
            (
                "andrew..marques@gmail.com",
                ["Wrong email format: andrew..marques@gmail.com"],
            ),
            (
                "andrew...marques@gmail.com",
                ["Wrong email format: andrew...marques@gmail.com"],
            ),
            (
                "andrew.@gmail..com",
                ["Wrong email format: andrew.@gmail..com"],
            ),
            # Email success cases
            ("andrew@gmail.com", []),
            ("andrew@gmail.com.br", []),
            ("andrew.marques@gmail.com", []),
            ("andrew!$%^&*@gmail.com", []),
        ],
    )
    def test_verify_errors_functional(
        self,
        email,
        expected,
    ):
        errors = []
        self.model._verify_errors(errors, email)

        assert errors == expected

    def test_get_guest_name_and_email_with_name_and_email(self):
        event = EventModel()
        name, email = event._get_guest_name_and_email("Some Name;email")

        assert name == "Some Name"
        assert email == "email"

    def test_get_guest_name_and_email_with_email_only(self):
        event = EventModel()
        name, email = event._get_guest_name_and_email("email")

        assert name == "Guest email"
        assert email == "email"

    @patch.object(EventModel, "_verify_errors")
    @patch.object(EventModel, "get_guests", return_value=["Some Name;email"])
    @patch.object(
        EventModel, "_get_guest_name_and_email", return_value=["Some Name", "email"]
    )
    def test_validate_guests_format_successfully(
        self, mock_get_guest_name_and_email, mock_get_guests, mock_verify_errors
    ):
        event = EventModel()

        event.validate_guests_format()

        mock_get_guests.assert_called_once()
        mock_get_guest_name_and_email.assert_called_once_with("Some Name;email")
        mock_verify_errors.assert_called_once_with([], "email")

    def test_get_guest_full_name_with_first_and_last_name(self):
        event = EventModel()
        name = "Some Name"

        assert event._get_guest_full_name(name) == ("Some", "Name")

    def test_get_guest_full_name_with_first_name_only(self):
        event = EventModel()
        name = "Some"

        assert event._get_guest_full_name(name) == ("Some", "")

    @patch.object(EventModel, "validate_guests_format")
    @patch.object(
        EventModel,
        "get_guests",
        return_value=["Some Name;email", "Some Name;email"],
    )
    @patch.object(
        EventModel, "_get_guest_name_and_email", return_value=["Some Name", "email"]
    )
    @patch.object(EventModel, "_get_guest_full_name", return_value=("Some", "Name"))
    @patch("apps.social.models.UserModel")
    @patch("apps.social.models.CreateUserPipeline")
    def test_create_guests(
        self,
        mock_create_user_pipeline,
        mock_user_model,
        mock_get_guest_full_name,
        mock_get_guest_name_and_email,
        mock_get_guests,
        mock_validate_guests_format,
    ):
        event = EventModel(service=ServiceModel())
        mock_user_model.objects.filter.return_value.exists.side_effect = [
            True,
            False,
        ]

        event.create_guests()

        mock_validate_guests_format.assert_called_once()
        mock_get_guests.assert_called_once()
        mock_get_guest_name_and_email.assert_has_calls(
            [call("Some Name;email"), call("Some Name;email")]
        )
        mock_get_guest_full_name.assert_has_calls(
            [call("Some Name"), call("Some Name")]
        )
        mock_user_model.objects.make_random_password.assert_called_once()
        mock_create_user_pipeline.assert_called_once_with(
            email="email",
            password=mock_user_model.objects.make_random_password.return_value,
            service=event.service,
            first_name="Some",
            last_name="Name",
            event=event,
            is_verified=True,
            send_mail=event.send_email_to_guests,
            email_type="guest_invitation",
        )
        mock_user_model.objects.filter.assert_has_calls(
            [
                call(email="email", event=event),
                call().exists(),
                call(email="email", event=event),
                call().exists(),
            ]
        )
        mock_create_user_pipeline.return_value.run.assert_called_once()


class TestAITextReportModel:
    @classmethod
    def setup_class(cls):
        cls.model = AITextReportModel

    def test_str(self):
        report = AITextReportModel(title="some title")

        assert str(report) == "some title"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "AI Text Report"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "AI Text Reports"

    def test_text_ai_choices(self):
        assert self.model.TEXT_AI_CHOICES == (
            ("dummy", "Dummy"),
            ("gpt-3", "GPT-3"),
        )

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255

    def test_pre_set_field(self):
        field = self.model._meta.get_field("pre_set")

        assert type(field) == models.TextField
        assert field.verbose_name == "Pre Set"

    def test_text_ai_field(self):
        field = self.model._meta.get_field("text_ai")

        assert type(field) == models.CharField
        assert field.verbose_name == "Text AI"
        assert field.max_length == 255
        assert field.choices == AITextReportModel.TEXT_AI_CHOICES
        assert field.default == "dummy"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 7

    @patch("apps.social.models.TEXT_AI")
    def test_text_ai_client(self, mock_text_ai):
        instance = self.model(text_ai="some_text_ai")
        result = instance.text_ai_client

        mock_text_ai.__getitem__.assert_called_once_with(instance.text_ai)
        assert result == mock_text_ai.__getitem__.return_value


class TestPostModel:
    @classmethod
    def setup_class(cls):
        cls.model = PostModel

    def test_str(self):
        post = PostModel(author=UserModel(first_name="John"))

        assert str(post) == "John's post"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Post"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Posts"

    def test_description_field(self):
        field = self.model._meta.get_field("description")

        assert type(field) == models.TextField
        assert field.verbose_name == "Description"
        assert field.null is True
        assert field.blank is True

    def test_attachment_field(self):
        field = self.model._meta.get_field("attachment")

        assert type(field) == models.FileField
        assert field.verbose_name == "Attachment"
        assert field.upload_to.__name__ == "post_attachment_directory_path"
        assert field.null is True
        assert field.blank is True

    def test_reactions_field(self):
        field = self.model._meta.get_field("reactions")

        assert type(field) == models.ManyToManyField
        assert field.related_model is ReactionModel
        assert field.verbose_name == "Reactions"
        assert field.remote_field.related_name == "posts"
        assert field.blank is True

    def test_author_field(self):
        field = self.model._meta.get_field("author")

        assert type(field) == models.ForeignKey
        assert field.related_model is UserModel
        assert field.verbose_name == "Author"
        assert field.remote_field.related_name == "posts"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model is ServiceModel
        assert field.verbose_name == "Service"
        assert field.remote_field.related_name == "posts"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_event_field(self):
        field = self.model._meta.get_field("event")

        assert type(field) == models.ForeignKey
        assert field.related_model is EventModel
        assert field.verbose_name == "Event"
        assert field.remote_field.related_name == "posts"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_ai_text_report_field(self):
        field = self.model._meta.get_field("ai_text_report")

        assert type(field) == models.ForeignKey
        assert field.related_model is AITextReportModel
        assert field.verbose_name == "AI Text Report"
        assert field.remote_field.related_name == "posts"
        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.null is True
        assert field.blank is True

    def test_ai_report_field(self):
        field = self.model._meta.get_field("ai_report")

        assert type(field) == models.TextField
        assert field.verbose_name == "AI Report"
        assert field.null is True
        assert field.blank is True

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 11

    def test_count_reactions(self):
        reaction = Mock(reaction_type=Mock())
        reaction.reaction_type.name = "Like"
        mock_self = Mock(reactions=Mock(all=Mock(return_value=[reaction])))

        result = PostModel.count_reactions(mock_self)

        mock_self.reactions.all.assert_called_once()
        assert result == {
            "Like": 1,
        }

    @patch.object(PostModel, "count_reactions", return_value={"Like": 1})
    def test_format_reactions_to_text(self, mock_count_reactions):
        instance = PostModel()

        result = instance.format_reactions_to_text()

        mock_count_reactions.assert_called_once()
        assert result == "Like: 1\n"

    def test_format_comments_to_text(self):
        mock_comment = Mock()
        mock_self = Mock(comments=Mock(all=Mock(return_value=[mock_comment])))

        result = PostModel.format_comments_to_text(mock_self)

        mock_self.comments.all.assert_called_once()
        assert result == (f"{mock_comment.author.first_name}: {mock_comment.content}\n")

    @patch.object(PostModel, "format_reactions_to_text")
    @patch.object(PostModel, "format_comments_to_text")
    def test_get_message_to_send(
        self, mock_format_comments_to_text, mock_format_reactions_to_text
    ):
        instance = PostModel()

        result = instance.get_message_to_send()

        mock_format_reactions_to_text.assert_called_once()
        mock_format_comments_to_text.assert_called_once()

        assert result == (
            f"""
        Post:

        {instance.description}

        Reactions:

        {mock_format_reactions_to_text.return_value}

        Comments:

        {mock_format_comments_to_text.return_value}
        """
        )

    def test_generate_ai_text_report(self):
        mock_self = Mock()

        PostModel.generate_ai_text_report(mock_self)

        mock_self.get_message_to_send.assert_called_once()
        mock_text_ai = mock_self.ai_text_report.text_ai_client
        mock_text_ai.assert_called_once_with(
            mock_self.ai_text_report.pre_set, mock_self.get_message_to_send.return_value
        )

        mock_client = mock_text_ai.return_value
        mock_client.get_response.assert_called_once()

        mock_self.save.assert_called_once()


class TestMissionTypeModel:
    @classmethod
    def setup_class(cls):
        cls.model = MissionTypeModel

    def test_str(self):
        mission_type = MissionTypeModel(name="foo")

        assert str(mission_type) == mission_type.name

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Mission Type"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Mission Types"

    def test_name_field(self):
        field = self.model._meta.get_field("name")

        assert type(field) == models.CharField
        assert field.verbose_name == "Name"
        assert field.max_length == 255
        assert field.unique is True

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 5


class TestMissionModel:
    @classmethod
    def setup_class(cls):
        cls.model = MissionModel

    def test_str(self):
        mission = MissionModel(title="foo")

        assert str(mission) == mission.title

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Mission"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Missions"

    def test_type_field(self):
        field = self.model._meta.get_field("type")

        assert type(field) == models.ManyToManyField
        assert field.verbose_name == "Type"
        assert field.remote_field.related_name == "missions"
        assert field.related_model is MissionTypeModel

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255

    def test_thumbnail_field(self):
        field = self.model._meta.get_field("thumbnail")

        assert type(field) == models.FileField
        assert field.verbose_name == "Thumbnail"
        assert field.upload_to.__name__ == "mission_directory_path"
        assert field.null is True
        assert field.blank is True
        assert field.help_text == (
            "Thumbnail for the mission video, if the attachment is a video"
        )

    def test_description_field(self):
        field = self.model._meta.get_field("description")

        assert type(field) == models.TextField
        assert field.verbose_name == "Description"
        assert field.null is True
        assert field.blank is True

    def test_attachment_field(self):
        field = self.model._meta.get_field("attachment")

        assert type(field) == models.FileField
        assert field.verbose_name == "Attachment"
        assert field.upload_to.__name__ == "mission_directory_path"
        assert field.null is True
        assert field.blank is True

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model is ServiceModel
        assert field.verbose_name == "Service"
        assert field.remote_field.related_name == "missions"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_service_client_field(self):
        field = self.model._meta.get_field("service_client")

        assert type(field) == models.ForeignKey
        assert field.related_model is ServiceClientModel
        assert field.verbose_name == "Client"
        assert field.remote_field.related_name == "missions"
        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.null is True
        assert field.blank is True

    def test_event_field(self):
        field = self.model._meta.get_field("event")

        assert type(field) == models.ForeignKey
        assert field.related_model is EventModel
        assert field.verbose_name == "Event"
        assert field.remote_field.related_name == "missions"
        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.null is True
        assert field.blank is True

    def test_order_field(self):
        field = self.model._meta.get_field("order")

        assert type(field) == models.IntegerField
        assert field.verbose_name == "Order"
        assert field.default == 0

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 12

    def test_get_completed_info(self):
        mock_user = Mock()
        mock_self = Mock()

        result = self.model.get_completed_info(mock_self, mock_user)

        mock_self.interactions.filter.assert_called_once_with(
            user=mock_user,
        )
        mock_self.interactions.filter.return_value.first.assert_called_once()

        assert result == (mock_self.interactions.filter.return_value.first.return_value)

    def test_is_completed(self):
        mock_user = Mock()
        mock_self = Mock()

        result = self.model.is_completed(mock_self, mock_user)

        mock_self.interactions.filter.assert_called_once_with(user=mock_user)

        mock_self.interactions.filter.return_value.exists.assert_called_once()

        assert result == (
            mock_self.interactions.filter.return_value.exists.return_value
        )

    @patch("apps.social.models.MissionInteractionModel")
    def test_complete(self, mock_mission_interaction_model):
        mock_self = Mock()
        mock_user = Mock()
        mock_attachment = Mock()
        mock_content = Mock()

        result = self.model.complete(
            mock_self, mock_user, mock_attachment, mock_content
        )

        mock_mission_interaction_model.objects.create.assert_called_once_with(
            user=mock_user,
            mission=mock_self,
            content=mock_content,
            attachment=mock_attachment,
        )

        assert result == (mock_mission_interaction_model.objects.create.return_value)


class TestMissionInteractionModel:
    @classmethod
    def setup_class(cls):
        cls.model = MissionInteractionModel

    def test_str(self):
        mission_interaction = MissionInteractionModel(
            mission=MissionModel(title="foo"), user=UserModel(first_name="bar")
        )

        assert str(mission_interaction) == "bar - foo"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "User Mission"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "User Missions"

    def test_mission_field(self):
        field = self.model._meta.get_field("mission")

        assert type(field) == models.ForeignKey
        assert field.related_model is MissionModel
        assert field.verbose_name == "Mission"
        assert field.remote_field.related_name == "interactions"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_user_field(self):
        field = self.model._meta.get_field("user")

        assert type(field) == models.ForeignKey
        assert field.related_model is UserModel
        assert field.verbose_name == "User"
        assert field.remote_field.related_name == "mission_interactions"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_attachment_field(self):
        field = self.model._meta.get_field("attachment")

        assert type(field) == models.FileField
        assert field.verbose_name == "Attachment"
        assert field.upload_to.__name__ == "mission_interaction_directory_path"
        assert field.null is True
        assert field.blank is True

    def test_content_field(self):
        field = self.model._meta.get_field("content")

        assert type(field) == models.TextField
        assert field.verbose_name == "Content"
        assert field.null is True
        assert field.blank is True

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 8


class TestLoginQuestions:
    @classmethod
    def setup_class(cls):
        cls.model = LoginQuestions

    def test_str(self):
        login_question = LoginQuestions(question="foo")

        assert str(login_question) == "foo"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Login Question"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Login Questions"

    def test_order_field(self):
        field = self.model._meta.get_field("order")

        assert type(field) == models.PositiveIntegerField
        assert field.verbose_name == "Order"
        assert field.default == 0

    def test_event_field(self):
        field = self.model._meta.get_field("event")

        assert type(field) == models.ForeignKey
        assert field.related_model is EventModel
        assert field.verbose_name == "Event"
        assert field.remote_field.related_name == "login_questions"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_question_field(self):
        field = self.model._meta.get_field("question")

        assert type(field) == models.CharField
        assert field.verbose_name == "Question"
        assert field.max_length == 255
        assert field.help_text == (
            "Tip: use the 'Save and add another' option to keep adding questions."
        )

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 7

    @patch("apps.social.models.LoginAnswer")
    def test_answer(self, mock_login_answer):
        mock_self = Mock()
        mock_user = Mock()
        mock_option = Mock()

        result = self.model.answer(mock_self, mock_user, mock_option)

        mock_login_answer.objects.create.assert_called_once_with(
            user=mock_user, question=mock_self, option=mock_option
        )

        assert result == (mock_login_answer.objects.create.return_value)

    def test_is_answered(self):
        mock_self = Mock()
        mock_user = Mock()

        result = self.model.is_answered(mock_self, mock_user)

        mock_self.answers.filter.assert_called_once_with(user=mock_user)
        mock_self.answers.filter.return_value.exists.assert_called_once_with()

        assert result == (mock_self.answers.filter.return_value.exists.return_value)


class TestLoginQuestionOption:
    @classmethod
    def setup_class(cls):
        cls.model = LoginQuestionOption

    def test_str(self):
        login_option = LoginQuestionOption()

        assert str(login_option) == "Option 0"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Login Question Option"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Login Question Options"

    def test_order_field(self):
        field = self.model._meta.get_field("order")

        assert type(field) == models.PositiveIntegerField
        assert field.verbose_name == "Order"
        assert field.default == 0

    def test_question_field(self):
        field = self.model._meta.get_field("question")

        assert type(field) == models.ForeignKey
        assert field.related_model is LoginQuestions
        assert field.verbose_name == "Question"
        assert field.remote_field.related_name == "options"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_option_field(self):
        field = self.model._meta.get_field("option")

        assert type(field) == models.CharField
        assert field.verbose_name == "Option"
        assert field.max_length == 255

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 7


class TestLoginAnswer:
    @classmethod
    def setup_class(cls):
        cls.model = LoginAnswer

    def test_str(self):
        login = LoginAnswer(option=LoginQuestionOption(option="Mock Option"))

        assert str(login) == "Mock Option"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Login Answer"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Login Answers"

    def test_user_field(self):
        field = self.model._meta.get_field("user")

        assert type(field) == models.ForeignKey
        assert field.verbose_name == "User"
        assert field.remote_field.related_name == "login_answers"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_question_field(self):
        field = self.model._meta.get_field("question")

        assert type(field) == models.ForeignKey
        assert field.verbose_name == "Question"
        assert field.remote_field.related_name == "answers"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_option_field(self):
        field = self.model._meta.get_field("option")

        assert type(field) == models.ForeignKey
        assert field.verbose_name == "Option"
        assert field.remote_field.related_name == "answers"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 7
