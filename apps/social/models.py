import re
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.service.models import ServiceClientModel, ServiceModel
from apps.social.chat_ai import TEXT_AI
from apps.user.models import UserModel
from pipelines.pipes import CreateUserPipeline
from pipelines.pipes.user import NotifyGuestNewPostPipeline
from utils.abstract_models.base_model import AttachmentModel, BaseModel


def get_formatted_datetime_now():
    date_now = datetime.now()
    date = date_now.strftime("%d/%m/%Y %H:%M:%S")
    return date


def post_attachment_directory_path(instance, filename):
    date = get_formatted_datetime_now()

    return f"media/posts/{instance.author.first_name}_{instance.id}_{date}_{filename}"


def event_directory_path(instance, filename):
    date = get_formatted_datetime_now()

    return f"media/event/{instance.title}_{instance.id}_{date}_{filename}"


def mission_interaction_directory_path(instance, filename):
    date = get_formatted_datetime_now()

    return (
        f"media/mission_interaction/{instance.user.id}_{instance.id}_{date}_{filename}"
    )


def mission_directory_path(instance, filename):
    date = get_formatted_datetime_now()

    return f"media/mission/{instance.title}_{instance.id}_{date}_{filename}"


class ReactionsMixin:
    @property
    def reactions_amount(self):
        return self.reactions.count()

    def react(self, user: UserModel, reaction_type_id: int):
        user_reaction = self.reactions.filter(user=user).first()
        if user_reaction:
            user_reaction.reaction_type_id = reaction_type_id
            user_reaction.save()
            return user_reaction
        return self.reactions.create(reaction_type_id=reaction_type_id, user=user)

    def get_reaction_by_user(self, user: UserModel):
        return self.reactions.filter(user=user).first()


class ReactionTypeModel(
    BaseModel, AttachmentModel(upload_to=post_attachment_directory_path).mixin
):
    REACTION_TYPE_CHOICES = (
        ("like", _("Like")),
        ("dislike", _("Dislike")),
        ("love", _("Love")),
        ("haha", _("Haha")),
        ("wow", _("Wow")),
        ("sad", _("Sad")),
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        choices=REACTION_TYPE_CHOICES,
    )
    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="reaction_types",
        on_delete=models.CASCADE,
    )
    clicked_image = models.ImageField(
        verbose_name=_("Clicked Image"),
        upload_to=post_attachment_directory_path,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Reaction Type")
        verbose_name_plural = _("Reaction Types")

    def __str__(self):
        return self.name


class ReactionModel(BaseModel):
    reaction_type = models.ForeignKey(
        ReactionTypeModel,
        verbose_name=_("Reaction Type"),
        related_name="reactions",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserModel,
        verbose_name=_("User"),
        related_name="reactions",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Reaction")
        verbose_name_plural = _("Reactions")

    def __str__(self):
        return self.reaction_type.name


class PostCommentModel(
    BaseModel,
    ReactionsMixin,
    AttachmentModel(upload_to=post_attachment_directory_path).mixin,
):
    content = models.TextField(verbose_name=_("Content"), null=True, blank=True)
    is_deleted = models.BooleanField(verbose_name=_("Is Deleted"), default=False)
    post = models.ForeignKey(
        "PostModel",
        verbose_name=_("Post"),
        related_name="comments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    answer = models.ForeignKey(
        "self",
        verbose_name=_("Answer"),
        related_name="answers",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    reactions = models.ManyToManyField(
        ReactionModel,
        verbose_name=_("Reactions"),
        related_name="comments",
        blank=True,
    )
    author = models.ForeignKey(
        UserModel,
        verbose_name=_("Author"),
        related_name="post_comments",
        on_delete=models.CASCADE,
    )
    mentions = models.ManyToManyField(
        UserModel,
        verbose_name=_("Mentions"),
        related_name="post_comments_mentions",
        blank=True,
    )

    @property
    def is_answer(self):
        return self.answer is not None

    class Meta:
        verbose_name = _("User Comment")
        verbose_name_plural = _("User Comments")

    def __str__(self):
        return f"{self.author.first_name}'s comment"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()


class EventModel(BaseModel, AttachmentModel(upload_to=event_directory_path).mixin):
    EVENT_TYPE = (
        ("open", "Open"),
        ("closed", "Closed"),
    )

    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
    )
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    event_type = models.CharField(
        verbose_name=_("Event Type"),
        max_length=255,
        choices=EVENT_TYPE,
        default="closed",
        help_text=_(
            'This property, when "Open", allows anyone to access the event. '
            'When "Closed", a certain group will only be able to access the '
            'event: fill in the "Guests" field in this case.'
        ),
    )
    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="events",
        on_delete=models.CASCADE,
    )
    service_client = models.ForeignKey(
        ServiceClientModel,
        verbose_name=_("Client"),
        related_name="events",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    guests = models.TextField(
        verbose_name=_("Guests"),
        null=True,
        blank=True,
        help_text="""
            Enter guests in the following format:
            <br>
            name;email,name;email,name;email,name;email,...
            <br>
            Like:
            <br>
            John Doe;john@mail.com,Elisa Jax;elisa@mail.com,Edward,edward.us@mail.com,...
        """,  # noqa: E501
    )
    send_email_to_guests = models.BooleanField(
        verbose_name=_("Send email to guests"),
        help_text=_("Send email to guests with their credentials"),
        default=False,
    )
    smtp_email = models.EmailField(verbose_name=_("SMTP Email"), null=True, blank=True)
    event_link = models.URLField(
        verbose_name=_("Event Link"),
        help_text=_("Link for guests to access the event"),
        null=True,
        blank=True,
    )
    require_login_answers = models.BooleanField(
        verbose_name=_("Require Login Answers"),
        default=False,
        help_text=_(
            "Go to 'Login Questions' session to add questions that will be "
            "asked to the guests before they can answer the event."
        ),
    )

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.title

    def get_guests(self):
        guests = self.guests
        result = []
        if guests:
            result = guests.split(",")
        return result

    @staticmethod
    def _verify_errors(errors: list, email: str):
        email_regex = (
            r"^([a-z0-9]+)[a-z0-9.-][^\.]*([a-z0-9!@#$%^&*()_+]+)"
            r"@([a-z0-9]+)[a-z0-9.-]*\.[a-z0-9]*([a-z0-9]+){2,}$"
        )

        if not re.match(email_regex, email):
            errors.append(f"Wrong email format: {email}")

    @staticmethod
    def _get_guest_name_and_email(guest):
        try:
            name, email = guest.split(";")
        except ValueError:
            email = guest
            name = f"Guest {email}"

        return name, email

    def validate_guests_format(self):
        guests = self.get_guests()
        if guests:
            errors = []

            for guest in guests:
                name, email = self._get_guest_name_and_email(guest)
                self._verify_errors(errors, email)

            if errors:
                raise ValidationError("; ".join(errors))  # pragma: no cover

    def _get_guest_full_name(self, name):
        full_name = name.split(" ")

        if len(full_name) == 1:
            return name, ""

        first_name = full_name[0]
        last_name = " ".join(full_name[1:])

        return first_name, last_name

    def create_guests(self):
        self.validate_guests_format()

        guests = self.get_guests()

        if guests:
            for guest in guests:
                name, email = self._get_guest_name_and_email(guest)
                first_name, last_name = self._get_guest_full_name(name.strip())
                user_exists_in_this_event = UserModel.objects.filter(
                    email=email, event=self
                ).exists()

                if not user_exists_in_this_event:
                    password_length = 6
                    only_digits = "0123456789"
                    password = UserModel.objects.make_random_password(
                        password_length, only_digits
                    )

                    pipeline = CreateUserPipeline(
                        email=email,
                        password=password,
                        service=self.service,
                        first_name=first_name,
                        last_name=last_name,
                        event=self,
                        is_verified=True,
                        send_mail=self.send_email_to_guests,
                        email_type="guest_invitation",
                    )
                    pipeline.run()


class AITextReportModel(BaseModel):
    TEXT_AI_CHOICES = (
        ("dummy", "Dummy"),
        ("gpt-3", "GPT-3"),
    )

    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
    )
    pre_set = models.TextField(verbose_name=_("Pre Set"))
    text_ai = models.CharField(
        verbose_name=_("Text AI"),
        max_length=255,
        choices=TEXT_AI_CHOICES,
        default="dummy",
    )

    @property
    def text_ai_client(self):
        return TEXT_AI[self.text_ai]

    class Meta:
        verbose_name = _("AI Text Report")
        verbose_name_plural = _("AI Text Reports")

    def __str__(self):
        return self.title


class PostModel(
    BaseModel,
    AttachmentModel(upload_to=post_attachment_directory_path).mixin,
    ReactionsMixin,
):
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)

    reactions = models.ManyToManyField(
        ReactionModel,
        verbose_name=_("Reactions"),
        related_name="posts",
        blank=True,
    )
    author = models.ForeignKey(
        UserModel,
        verbose_name=_("Author"),
        related_name="posts",
        on_delete=models.CASCADE,
    )
    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="posts",
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        EventModel,
        verbose_name=_("Event"),
        related_name="posts",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    ai_text_report = models.ForeignKey(
        AITextReportModel,
        verbose_name=_("AI Text Report"),
        related_name="posts",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    ai_report = models.TextField(
        verbose_name=_("AI Report"),
        null=True,
        blank=True,
    )

    def count_reactions(self):
        reactions = self.reactions.all()

        reactions_count = {}

        for reaction in reactions:
            reactions_count[reaction.reaction_type.name] = (
                reactions_count.get(reaction.reaction_type.name, 0) + 1
            )

        return reactions_count

    def format_reactions_to_text(self):
        reactions = self.count_reactions()

        result = ""

        for reaction_type, reaction_count in reactions.items():
            result += f"{reaction_type}: {reaction_count}\n"

        return result

    def format_comments_to_text(self):
        comments = self.comments.filter(is_deleted=False, author__is_staff=False)[:3]

        result = ""

        for comment in comments:
            result += f"{comment.author.first_name}: {comment.content}\n"

        return result

    def get_message_to_send(self):
        reactions = self.format_reactions_to_text()
        comments = self.format_comments_to_text()

        return f"""
        Post:

        {self.description}

        Reactions:

        {reactions}

        Comments:

        {comments}
        """

    def generate_ai_text_report(self):
        if self.ai_text_report:
            text_ai = self.ai_text_report.text_ai_client
            message = self.get_message_to_send()
            client = text_ai(self.ai_text_report.pre_set, message)

            self.ai_report = client.get_response()
            self.save()

    def notify_new_post(self):
        if self.event:
            guests = self.event.users.filter(is_active=True)

            for guest in guests:
                pipeline = NotifyGuestNewPostPipeline(user=guest)
                pipeline.run()

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __str__(self):
        return f"{self.author.first_name}'s post"


class MissionTypeModel(BaseModel):
    MISSION_TYPE_CHOICES = (
        ("Video", "Video"),
        ("Image", "Image"),
        ("Audio", "Audio"),
        ("Text", "Text"),
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        unique=True,
        choices=MISSION_TYPE_CHOICES,
    )

    class Meta:
        verbose_name = _("Mission Type")
        verbose_name_plural = _("Mission Types")

    def __str__(self):
        return self.name


class MissionModel(BaseModel, AttachmentModel(upload_to=mission_directory_path).mixin):
    type = models.ManyToManyField(
        MissionTypeModel,
        verbose_name=_("Type"),
        related_name="missions",
    )
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
    )
    thumbnail = models.FileField(
        verbose_name=_("Thumbnail"),
        upload_to=mission_directory_path,
        null=True,
        blank=True,
        help_text=_("Thumbnail for the mission video, if the attachment is a video"),
    )
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="missions",
        on_delete=models.CASCADE,
    )
    service_client = models.ForeignKey(
        ServiceClientModel,
        verbose_name=_("Client"),
        related_name="missions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    event = models.ForeignKey(
        EventModel,
        verbose_name=_("Event"),
        related_name="missions",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(verbose_name=_("Order"), default=0)

    def get_completed_info(self, user: UserModel):
        return self.interactions.filter(user=user).first()

    def is_completed(self, user: UserModel):
        return self.interactions.filter(user=user).exists()

    def complete(self, user: UserModel, attachment=None, content=None):
        return MissionInteractionModel.objects.create(
            user=user,
            mission=self,
            content=content,
            attachment=attachment,
        )

    class Meta:
        verbose_name = _("Mission")
        verbose_name_plural = _("Missions")

    def __str__(self):
        return self.title


class MissionInteractionModel(
    BaseModel, AttachmentModel(upload_to=mission_interaction_directory_path).mixin
):
    mission = models.ForeignKey(
        MissionModel,
        verbose_name=_("Mission"),
        related_name="interactions",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserModel,
        verbose_name=_("User"),
        related_name="mission_interactions",
        on_delete=models.CASCADE,
    )
    content = models.TextField(verbose_name=_("Content"), null=True, blank=True)

    class Meta:
        verbose_name = _("User Mission")
        verbose_name_plural = _("User Missions")

    def __str__(self):
        return f"{self.user.first_name} - {self.mission.title}"


class LoginQuestions(BaseModel):
    order = models.PositiveIntegerField(verbose_name=_("Order"), default=0)
    event = models.ForeignKey(
        EventModel,
        verbose_name=_("Event"),
        related_name="login_questions",
        on_delete=models.CASCADE,
    )
    question = models.CharField(
        verbose_name=_("Question"),
        max_length=255,
        help_text=_(
            "Tip: use the 'Save and add another' option to keep adding questions."
        ),
    )

    class Meta:
        verbose_name = _("Login Question")
        verbose_name_plural = _("Login Questions")

    def answer(self, user: UserModel, option):
        return LoginAnswer.objects.create(
            user=user,
            question=self,
            option=option,
        )

    def is_answered(self, user: UserModel):
        return self.answers.filter(user=user).exists()

    def __str__(self):
        return self.question


class LoginQuestionOption(BaseModel):
    order = models.PositiveIntegerField(verbose_name=_("Order"), default=0)
    question = models.ForeignKey(
        LoginQuestions,
        related_name="options",
        verbose_name=_("Question"),
        on_delete=models.CASCADE,
    )
    option = models.CharField(verbose_name=_("Option"), max_length=255)

    class Meta:
        verbose_name = _("Login Question Option")
        verbose_name_plural = _("Login Question Options")

    def __str__(self):
        return f"Option {self.order}"


class LoginAnswer(BaseModel):
    user = models.ForeignKey(
        UserModel,
        verbose_name=_("User"),
        related_name="login_answers",
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        LoginQuestions,
        related_name="answers",
        verbose_name=_("Question"),
        on_delete=models.CASCADE,
    )
    option = models.ForeignKey(
        LoginQuestionOption,
        related_name="answers",
        verbose_name=_("Option"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Login Answer")
        verbose_name_plural = _("Login Answers")

    def __str__(self):
        return str(self.option.option)
