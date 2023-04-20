import random
import re
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.service.models import ServiceModel
from apps.user.models import UserModel
from pipelines.pipes import CreateUserPipeline
from utils.abstract_models.base_model import BaseModel


def post_attachment_directory_path(instance, filename):
    date_now = datetime.now()
    date = date_now.strftime("%d%m%Y_%H:%M:%S")

    return (
        f"media/posts/{instance.author.first_name}_"
        f"{instance.id}_{date}_{filename}"
    )


def event_directory_path(instance, filename):
    date_now = datetime.now()
    date = date_now.strftime("%d%m%Y_%H:%M:%S")

    return f"media/event/{instance.name}_" f"{instance.id}_{date}_{filename}"


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
        return self.reactions.create(
            reaction_type_id=reaction_type_id, user=user
        )

    def unreact(self, user: UserModel):
        user_reaction = self.reactions.filter(user=user)
        if user_reaction:
            user_reaction.delete()


class ReactionTypeModel(BaseModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    attachment = models.FileField(
        verbose_name=_("Attachment"),
        upload_to=post_attachment_directory_path,
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="reaction_types",
        on_delete=models.CASCADE,
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


class PostCommentModel(BaseModel, ReactionsMixin):
    content = models.TextField(
        verbose_name=_("Content"), null=True, blank=True
    )
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

    @property
    def is_answer(self):
        return self.answer is not None

    class Meta:
        verbose_name = _("Post Comment")
        verbose_name_plural = _("Post Comments")

    def __str__(self):
        return f"{self.author.first_name}'s comment"


class EventModel(BaseModel):
    EVENT_TYPE = (
        ("open", "Open"),
        ("closed", "Closed"),
    )

    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_("Description"), null=True, blank=True
    )
    attachment = models.FileField(
        verbose_name=_("Attachment"),
        upload_to=event_directory_path,
        null=True,
        blank=True,
    )
    event_type = models.CharField(
        verbose_name=_("Event Type"),
        max_length=255,
        choices=EVENT_TYPE,
        default="closed",
    )
    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="events",
        on_delete=models.CASCADE,
    )
    guests = models.TextField(
        verbose_name=_("Guests"),
        null=True,
        blank=True,
        help_text="""
            Enter guests in the following format:
            <br>
            email,password<br>
            email,password<br>
            email,password<br>
            ...
        """,
    )
    send_email_to_guests = models.BooleanField(
        verbose_name=_("Send email to guests"),
        help_text=_("Send email to guests with their credentials"),
        default=False,
    )
    event_link = models.URLField(
        verbose_name=_("Event Link"),
        help_text=_("Link for guests to access the event"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.title

    def get_guests(self):
        guests = self.guests
        guests = guests.replace("\r", "")
        result = []
        if guests:
            result = guests.split("\n")
        return result

    @staticmethod
    def _verify_errors(
        errors: list, email: str, password: str, line_number: str
    ):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        password_regex = r"^[a-zA-Z0-9!@#$%^&*()_+]+$"

        if not re.match(email_regex, email):
            errors.append(f"{line_number} Wrong email format: {email}")
        if not re.match(password_regex, password):
            errors.append(f"{line_number} Wrong password format: {password}")

    def validate_guests_format(self):
        guests = self.get_guests()
        if guests:
            errors = []

            for index, guest in enumerate(guests):
                line_number = f"Line: {index + 1}:: "
                try:
                    email, password = guest.split(",")
                except ValueError:
                    errors.append(f"{line_number} Wrong line format: {guest}")
                    continue

                self._verify_errors(errors, email, password, line_number)

            if errors:
                raise ValidationError("; ".join(errors))

    def clean(self):
        self.validate_guests_format()

        guests = self.get_guests()

        if guests:
            for guest in guests:
                email, password = guest.split(",")
                user_exists_in_this_event = UserModel.objects.filter(
                    email=email, event=self
                ).exists()
                if not user_exists_in_this_event:
                    pipeline = CreateUserPipeline(
                        email=email,
                        password=password,
                        service=self.service,
                        first_name=f"Guest {random.randint(10000, 99999)}",
                        last_name=self.title,
                        event=self,
                        is_verified=True,
                        send_mail=self.send_email_to_guests,
                    )
                    pipeline.run()


class PostModel(BaseModel, ReactionsMixin):
    description = models.TextField(
        verbose_name=_("Description"), null=True, blank=True
    )
    attachment = models.FileField(
        verbose_name=_("Attachment"),
        upload_to=post_attachment_directory_path,
        null=True,
        blank=True,
    )

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

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __str__(self):
        return f"{self.author.first_name}'s post"
