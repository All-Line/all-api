from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.service.models import ServiceModel
from apps.user.managers import UserForRetentionManager, UserManager


def profile_image_directory_path(instance, filename):
    date_now = datetime.now()
    date = date_now.strftime("%d%m%Y_%H:%M:%S")

    return f"media/{instance.first_name}_{date}_{filename}"


class UserModel(AbstractUser):
    groups = None
    user_permissions = None
    objects = UserManager()

    is_verified = models.BooleanField(verbose_name=_("Is Verified"), default=False)
    is_premium = models.BooleanField(verbose_name=_("Is Premium"), default=False)
    is_deleted = models.BooleanField(verbose_name=_("Is Deleted"), default=False)
    document = models.CharField(
        verbose_name=_("Document"), max_length=255, null=True, blank=True
    )
    email = models.EmailField(verbose_name=_("Email Address"))
    first_name = models.CharField(verbose_name=_("First Name"), max_length=30)
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=30)
    username = models.CharField(
        verbose_name=_("Username"),
        max_length=150,
        unique=True,
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        null=True,
        blank=True,
    )
    birth_date = models.DateField(verbose_name=_("Birth Date"), null=True, blank=True)
    last_login = models.DateTimeField(
        verbose_name=_("Last Login"), null=True, blank=True
    )
    country = models.CharField(
        verbose_name=_("Country"), max_length=255, null=True, blank=True
    )
    profile_image = models.FileField(
        verbose_name=_("Profile Image"),
        upload_to=profile_image_directory_path,
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="users",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    delete_reason = models.TextField(
        verbose_name=_("Delete Reason"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        unique_together = ["document", "service"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def can_access(self, course):
        if course.is_paid:
            contracts_amount = (
                self.contracts.only("id")
                .filter(package__courses__in=[course], is_active=True)
                .count()
            )
            return contracts_amount > 0
        return True


class UserForRetentionProxy(UserModel):
    objects = UserForRetentionManager()

    class Meta:
        proxy = True
        verbose_name = _("User for retention")
        verbose_name_plural = _("Users for retention")
