from unittest.mock import Mock, patch

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.service.models import ServiceModel
from apps.user.managers import UserForRetentionManager, UserManager
from apps.user.models import (
    UserForRetentionProxy,
    UserModel,
    delete_old_profile_image,
    profile_image_directory_path,
)


class TestUserModel:
    @classmethod
    def setup_class(cls):
        cls.model = UserModel

    def test_str(self):
        user = UserModel(first_name="first_name", last_name="last_name")

        assert str(user) == "first_name last_name"

    def test_parent_class(self):
        assert issubclass(self.model, AbstractUser)

    def test_objects(self):
        assert self.model.objects == UserManager()

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "User"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Users"

    def test_override_fields(self):
        groups = self.model.groups
        user_permissions = self.model.user_permissions

        assert groups is None
        assert user_permissions is None

    def test_is_verified_field(self):
        field = self.model._meta.get_field("is_verified")

        assert type(field) == models.BooleanField
        assert field.verbose_name == "Is Verified"
        assert field.default is False

    def test_is_premium_field(self):
        field = self.model._meta.get_field("is_premium")

        assert type(field) == models.BooleanField
        assert field.verbose_name == "Is Premium"
        assert field.default is False

    def test_is_deleted_field(self):
        field = self.model._meta.get_field("is_deleted")

        assert type(field) == models.BooleanField
        assert field.verbose_name == "Is Deleted"
        assert field.default is False

    def test_document_field(self):
        field = self.model._meta.get_field("document")

        assert type(field) == models.CharField
        assert field.verbose_name == "Document"
        assert field.max_length == 255
        assert field.null is True
        assert field.blank is True

    def test_birth_date_field(self):
        field = self.model._meta.get_field("birth_date")

        assert type(field) == models.DateField
        assert field.verbose_name == "Birth Date"
        assert field.null is True
        assert field.blank is True

    def test_last_login_field(self):
        field = self.model._meta.get_field("last_login")

        assert type(field) == models.DateTimeField
        assert field.verbose_name == "Last Login"
        assert field.null is True
        assert field.blank is True

    def test_country_field(self):
        field = self.model._meta.get_field("country")

        assert type(field) == models.CharField
        assert field.verbose_name == "Country"
        assert field.max_length == 255
        assert field.null is True
        assert field.blank is True

    def test_profile_image_field(self):
        field = self.model._meta.get_field("profile_image")

        assert type(field) == models.FileField
        assert field.verbose_name == "Profile Image"
        assert field.upload_to.__name__ == "profile_image_directory_path"
        assert field.null is True
        assert field.blank is True

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model is ServiceModel
        assert field.verbose_name == "Service"
        assert field.remote_field.related_name == "users"
        assert field.null is True
        assert field.blank is True
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_delete_reason_field(self):
        field = self.model._meta.get_field("delete_reason")

        assert type(field) == models.TextField
        assert field.verbose_name == "Delete Reason"
        assert field.null is True
        assert field.blank is True

    def test_email_field(self):
        field = self.model._meta.get_field("email")

        assert type(field) == models.EmailField
        assert field.verbose_name == "Email Address"

    def test_first_name_field(self):
        field = self.model._meta.get_field("first_name")

        assert type(field) == models.CharField
        assert field.verbose_name == "First Name"
        assert field.max_length == 30

    def test_last_name_field(self):
        field = self.model._meta.get_field("last_name")

        assert type(field) == models.CharField
        assert field.verbose_name == "Last Name"
        assert field.max_length == 30

    def test_username_field(self):
        field = self.model._meta.get_field("username")

        assert type(field) == models.CharField
        assert field.verbose_name == "Username"
        assert field.max_length == 150
        assert field.unique is True
        assert field.validators[0] == AbstractUser.username_validator
        assert field.null is True
        assert field.blank is True

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 21

    def test_can_access_with_paid_course(self):
        course = Mock(is_paid=True)
        contracts = Mock()
        contracts.only.return_value.filter.return_value.count.return_value = 1

        user = UserModel
        mock_self = Mock(contracts=contracts)
        result = user.can_access(mock_self, course)

        contracts.only.assert_called_once_with("id")
        contracts.only.return_value.filter.assert_called_once_with(
            package__courses__in=[course], is_active=True
        )
        contracts.only.return_value.filter.return_value.count.assert_called_once()
        assert result is True

    def test_can_access_with_not_paid_course(self):
        course = Mock(is_paid=False)

        user = UserModel
        mock_self = Mock()
        result = user.can_access(mock_self, course)

        assert result is True

    def test_is_guest(self):
        user = UserModel()
        assert user.is_guest is False

    @patch("apps.user.models.S3Boto3Storage")
    def test_delete_old_profile_image_receiver(self, mock_storage):
        instance = Mock()
        sender = Mock()
        instance.profile_image = "profile_image.jpg"
        delete_old_profile_image(sender, instance)

        sender.objects.get.assert_called_once_with(pk=instance.pk)

        mock_storage.assert_called_once()
        mock_storage.return_value.exists.assert_called_once_with(
            sender.objects.get.return_value.profile_image.name
        )
        mock_storage.return_value.delete.assert_called_once_with(
            sender.objects.get.return_value.profile_image.name
        )


class TestUserForRetentionProxy:
    @classmethod
    def setup_class(cls):
        cls.proxy = UserForRetentionProxy

    def test_parent_class(self):
        assert issubclass(self.proxy, UserModel)

    def test_objects(self):
        assert self.proxy.objects == UserForRetentionManager()

    def test_meta_proxy(self):
        assert self.proxy._meta.proxy is True

    def test_meta_verbose_name(self):
        assert self.proxy._meta.verbose_name == "User for retention"

    def test_meta_verbose_name_plural(self):
        assert self.proxy._meta.verbose_name_plural == "Users for retention"


@patch("apps.user.models.datetime")
def test_profile_image_directory_path(mock_datetime):
    instance = Mock()
    filename = Mock()
    result = profile_image_directory_path(instance, filename)

    mock_datetime.now.assert_called_once()
    mock_datetime.now.return_value.strftime.assert_called_once_with(
        "%d%m%Y_%H:%M:%S"
    )

    assert result == (
        f"media/{instance.first_name}_"
        f"{mock_datetime.now.return_value.strftime.return_value}_"
        f"{filename}"
    )
