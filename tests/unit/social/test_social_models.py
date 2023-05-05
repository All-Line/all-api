from unittest.mock import Mock, call, patch

import pytest
from django.core.exceptions import ValidationError
from django.db import models

from apps.service.models import ServiceModel
from apps.social.models import (
    AITextReportModel,
    EventModel,
    LoginAnswer,
    LoginQuestionOption,
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
        assert self.model._meta.verbose_name == "Post Comment"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Post Comments"

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
            email,password<br>
            email,password<br>
            email,password<br>
            ...
        """
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
        assert len(self.model._meta.fields) == 14

    def test_get_guests(self):
        event = EventModel(guests="email1,password1\nemail2,password2")

        assert event.get_guests() == [
            "email1,password1",
            "email2,password2",
        ]

    def test_verify_errors(self):
        errors = []
        line_number = "0"
        email = "wrong_email.com"
        password = "//"

        self.model._verify_errors(errors, email, password, line_number)

        assert errors == [
            "0 Wrong email format: wrong_email.com",
            "0 Wrong password format: //",
        ]

    @pytest.mark.parametrize(
        "email, password, line_number, expected",
        [
            # Email fail cases
            (
                "andrew.com",
                "change1234",
                "0",
                ["0 Wrong email format: andrew.com"],
            ),
            (
                "andrew@.com",
                "change1234",
                "0",
                ["0 Wrong email format: andrew@.com"],
            ),
            (
                "andrew@gmail.c",
                "change1234",
                "0",
                ["0 Wrong email format: andrew@gmail.c"],
            ),
            (
                "andrew@com",
                "change1234",
                "0",
                ["0 Wrong email format: andrew@com"],
            ),
            (
                "andrew@com.",
                "change1234",
                "0",
                ["0 Wrong email format: andrew@com."],
            ),
            (
                "andrew@gmail",
                "change1234",
                "0",
                ["0 Wrong email format: andrew@gmail"],
            ),
            (
                "andrew@gmail.",
                "change1234",
                "0",
                ["0 Wrong email format: andrew@gmail."],
            ),
            (
                "andrew@gmail!",
                "change1234",
                "0",
                ["0 Wrong email format: andrew@gmail!"],
            ),
            (
                "andrew@$gmail.com",
                "change1234",
                "0",
                ["0 Wrong email format: andrew@$gmail.com"],
            ),
            (
                ".andrew@gmail.com",
                "change1234",
                "0",
                ["0 Wrong email format: .andrew@gmail.com"],
            ),
            (
                "andrew..marques@gmail.com",
                "change1234",
                "0",
                ["0 Wrong email format: andrew..marques@gmail.com"],
            ),
            (
                "andrew...marques@gmail.com",
                "change1234",
                "0",
                ["0 Wrong email format: andrew...marques@gmail.com"],
            ),
            (
                "andrew.@gmail..com",
                "change1234",
                "0",
                ["0 Wrong email format: andrew.@gmail..com"],
            ),
            # Email success cases
            ("andrew@gmail.com", "change1234", "0", []),
            ("andrew@gmail.com.br", "change1234", "0", []),
            ("andrew.marques@gmail.com", "change1234", "0", []),
            ("andrew!$%^&*@gmail.com", "change1234", "0", []),
        ],
    )
    def test_verify_errors_functional(
        self,
        email,
        password,
        line_number,
        expected,
    ):
        errors = []
        self.model._verify_errors(errors, email, password, line_number)

        assert errors == expected

    @patch.object(EventModel, "_verify_errors")
    @patch.object(EventModel, "get_guests", return_value=["email,password"])
    def test_validate_guests_format_successfully(
        self, mock_get_guests, mock_verify_errors
    ):
        event = EventModel()

        event.validate_guests_format()

        mock_get_guests.assert_called_once()
        mock_verify_errors.assert_called_once_with(
            [], "email", "password", "Line: 1:: "
        )

    @patch.object(EventModel, "_verify_errors")
    @patch.object(EventModel, "get_guests", return_value=["email", "email,password"])
    def test_validate_guests_format_with_errors(
        self, mock_get_guests, mock_verify_errors
    ):
        event = EventModel()

        with pytest.raises(ValidationError):
            event.validate_guests_format()

        mock_get_guests.assert_called_once()
        mock_verify_errors.assert_called_once_with(
            ["Line: 1::  Wrong line format: email"],
            "email",
            "password",
            "Line: 2:: ",
        )

    @patch.object(EventModel, "validate_guests_format")
    @patch.object(
        EventModel,
        "get_guests",
        return_value=["email,password", "email,password"],
    )
    @patch("apps.social.models.UserModel")
    @patch("apps.social.models.CreateUserPipeline")
    @patch("apps.social.models.random")
    def test_clean(
        self,
        mock_random,
        mock_create_user_pipeline,
        mock_user_model,
        mock_get_guests,
        mock_validate_guests_format,
    ):
        event = EventModel(service=ServiceModel())
        mock_user_model.objects.filter.return_value.exists.side_effect = [
            True,
            False,
        ]

        event.clean()

        mock_get_guests.assert_called_once()
        mock_validate_guests_format.assert_called_once()
        mock_create_user_pipeline.assert_called_once_with(
            email="email",
            password="password",
            service=event.service,
            first_name=f"Guest {mock_random.randint.return_value}",
            last_name=event.title,
            event=event,
            is_verified=True,
            send_mail=event.send_email_to_guests,
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

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 12


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
        assert len(self.model._meta.fields) == 12
