from unittest.mock import Mock, patch

from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet

from apps.user.permissions import UserPermissions
from apps.user.serializers import (
    CreateUserSerializer,
    LoginSerializer,
    UserDataSerializer,
    UserForRetentionSerializer,
)
from apps.user.views import UserViewSet
from utils.auth import BearerTokenAuthentication
from utils.mixins.multiserializer import MultiSerializerMixin


class TestUserViewSet:
    @classmethod
    def setup_class(cls):
        cls.view = UserViewSet()

    def test_parent_class(self):
        assert issubclass(UserViewSet, mixins.CreateModelMixin)
        assert issubclass(UserViewSet, GenericViewSet)
        assert issubclass(UserViewSet, MultiSerializerMixin)

    def test_authentication_classes(self):
        assert self.view.authentication_classes == [BearerTokenAuthentication]

    def test_permission_classes(self):
        assert self.view.permission_classes == [UserPermissions]

    def test_serializers_attr(self):
        assert self.view.serializers == {
            "create": CreateUserSerializer,
            "me": UserDataSerializer,
            "update_me": UserDataSerializer,
            "login": LoginSerializer,
            "delete_me": UserForRetentionSerializer,
        }

    @patch("apps.user.views.super")
    def test_create(self, mock_super):
        request = Mock()
        result = self.view.create(request)

        mock_super.assert_called_once()
        mock_super.return_value.create.assert_called_once_with(request)

        assert result == mock_super.return_value.create.return_value

    @patch("apps.user.views.Response")
    @patch("apps.user.views.UserViewSet.get_serializer")
    def test_me(self, mock_get_serializer, mock_response):
        request = Mock()
        result = self.view.me(request)

        mock_get_serializer.assert_called_once_with(request.user)
        mock_response.assert_called_once_with(
            mock_get_serializer.return_value.data
        )
        assert result == mock_response.return_value

    @patch("apps.user.views.Response")
    @patch("apps.user.views.UserViewSet.get_serializer")
    def test_update_me(self, mock_get_serializer, mock_response):
        request = Mock(user="user")
        result = self.view.update_me(request)

        mock_get_serializer.assert_called_once_with(
            request.user, data=request.data, partial=True
        )
        mock_get_serializer.return_value.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_get_serializer.return_value.save.assert_called_once()

        mock_response.assert_called_once_with(
            mock_get_serializer.return_value.data
        )
        assert result == mock_response.return_value

    @patch("apps.user.views.Response")
    @patch("apps.user.views.AuthenticatedUserSerializer")
    @patch("apps.user.views.UserViewSet.get_serializer")
    def test_login(
        self,
        mock_get_serializer,
        mock_authenticated_user_serializer,
        mock_response,
    ):
        request = Mock()

        result = self.view.login(request)

        mock_get_serializer.assert_called_once_with(data=request.data)
        mock_get_serializer.return_value.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_authenticated_user_serializer.assert_called_once_with(
            mock_get_serializer.return_value.user
        )
        mock_response.assert_called_once_with(
            mock_authenticated_user_serializer.return_value.data
        )
        assert result == mock_response.return_value

    @patch("apps.user.views.Response")
    @patch("apps.user.views.UserViewSet.get_serializer")
    def test_delete_me(self, mock_get_serializer, mock_response):
        mock_request = Mock(data={"delete_reason": "delete test"})
        result = self.view.delete_me(mock_request)

        mock_get_serializer.assert_called_once_with(data=mock_request.data)
        mock_get_serializer.return_value.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_request.user.save.assert_called_once()
        mock_response.assert_called_once_with(
            status=status.HTTP_204_NO_CONTENT
        )
        assert mock_request.user.delete_reason == "delete test"
        assert mock_request.user.is_deleted is True
        assert mock_request.user.is_active is False
        assert result == mock_response.return_value

    @patch("apps.user.views.Response")
    @patch("apps.user.views.Token")
    def test_confirm_email_failure_with_token_does_not_exist(
        self, mock_token, mock_response
    ):
        token = "foo"
        mock_token.DoesNotExist = Exception
        mock_token.objects.select_related.return_value.only.return_value.get.side_effect = (  # noqa: E501
            Exception()
        )

        result = self.view.confirm_email(None, token)
        select_related = mock_token.objects.select_related.return_value

        mock_token.objects.select_related.assert_called_once_with("user")
        select_related.only.assert_called_once_with("user", "created")
        select_related.only.return_value.get.assert_called_once_with(key=token)
        mock_response.assert_called_once_with(
            {"detail": "This link is expired"}, status=410
        )
        assert result == mock_response.return_value

    @patch("apps.user.views.Response")
    @patch("apps.user.views.timezone")
    @patch("apps.user.views.timedelta")
    @patch("apps.user.views.Token")
    def test_confirm_email_failure_with_token_expired(
        self, mock_token, mock_timedelta, mock_timezone, mock_response
    ):
        token_key = "foo"
        request = {}
        token = (
            mock_token.objects.select_related.return_value.only.return_value.get.return_value  # noqa: E501
        )
        user = token.user
        service = user.service
        filtered_email_config = (
            service.email_configs.only.return_value.filter.return_value
        )
        email_config = filtered_email_config.first.return_value
        mock_timedelta.return_value = 1
        mock_token.objects.select_related.return_value.only.return_value.get.return_value.created = (  # noqa: E501
            1
        )
        mock_timezone.now.return_value = 3

        result = self.view.confirm_email(request, token_key)
        select_related = mock_token.objects.select_related.return_value

        mock_token.objects.select_related.assert_called_once_with("user")
        select_related.only.assert_called_once_with("user", "created")
        select_related.only.return_value.get.assert_called_once_with(
            key=token_key
        )
        service.email_configs.only.assert_called_once_with(
            "email_link_expiration"
        )
        service.email_configs.only.return_value.filter.assert_called_once_with(
            email_config_type="register"
        )
        service.email_configs.only.return_value.filter.return_value.first.assert_called_once()  # noqa: E501
        mock_timedelta.assert_called_once_with(
            hours=email_config.email_link_expiration
        )
        mock_timezone.now.assert_called_once()
        token.delete.assert_called_once()
        user.delete.assert_called_once()
        mock_response.assert_called_once_with(
            {"detail": "This link is expired"}, status=410
        )
        assert result == mock_response.return_value

    @patch("apps.user.views.Response")
    @patch("apps.user.views.timezone")
    @patch("apps.user.views.timedelta")
    @patch("apps.user.views.Token")
    def test_confirm_email_successfully_without_email_config(
        self, mock_token, mock_timedelta, mock_timezone, mock_response
    ):
        token_key = "foo"
        token = (
            mock_token.objects.select_related.return_value.only.return_value.get.return_value  # noqa: E501
        )
        user = token.user
        service = user.service
        service.email_configs.only.return_value.filter.return_value.first.return_value = (  # noqa: E501
            None
        )
        request = {}
        mock_timedelta.return_value = 1
        mock_token.objects.select_related.return_value.only.return_value.get.return_value.created = (  # noqa: E501
            1
        )
        mock_timezone.now.return_value = 1

        result = self.view.confirm_email(request, token_key)

        select_related = mock_token.objects.select_related.return_value
        mock_token.objects.select_related.assert_called_once_with("user")
        select_related.only.assert_called_once_with("user", "created")
        select_related.only.return_value.get.assert_called_once_with(  # noqa: E501
            key=token_key
        )
        service.email_configs.only.assert_called_once_with(
            "email_link_expiration"
        )
        service.email_configs.only.return_value.filter.assert_called_once_with(
            email_config_type="register"
        )
        service.email_configs.only.return_value.filter.return_value.first.assert_called_once()  # noqa: E501
        mock_timedelta.assert_called_once_with(hours=1)
        mock_timezone.now.assert_called_once()
        token.delete.assert_called_once()
        user.delete.assert_not_called()
        mock_token.objects.create.assert_called_once_with(user=user)
        user.save.assert_called_once()
        mock_response.assert_called_once_with(status=204)
        assert user.is_verified is True
        assert result == mock_response.return_value

    @patch("apps.user.views.Response")
    @patch("apps.user.views.timezone")
    @patch("apps.user.views.timedelta")
    @patch("apps.user.views.Token")
    def test_confirm_email_successfully_with_email_config(
        self, mock_token, mock_timedelta, mock_timezone, mock_response
    ):
        token_key = "foo"
        token = (
            mock_token.objects.select_related.return_value.only.return_value.get.return_value  # noqa: E501
        )
        user = token.user
        service = user.service
        filtered_email_config = (
            service.email_configs.only.return_value.filter.return_value
        )
        email_config = filtered_email_config.first.return_value
        request = {}
        mock_timedelta.return_value = 1
        mock_token.objects.select_related.return_value.only.return_value.get.return_value.created = (  # noqa: E501
            1
        )
        mock_timezone.now.return_value = 1

        result = self.view.confirm_email(request, token_key)

        select_related = mock_token.objects.select_related.return_value

        mock_token.objects.select_related.assert_called_once_with("user")
        select_related.only.assert_called_once_with("user", "created")
        select_related.only.return_value.get.assert_called_once_with(
            key=token_key
        )
        service.email_configs.only.assert_called_once_with(
            "email_link_expiration"
        )
        service.email_configs.only.return_value.filter.assert_called_once_with(
            email_config_type="register"
        )
        service.email_configs.only.return_value.filter.return_value.first.assert_called_once()  # noqa: E501
        mock_timedelta.assert_called_once_with(
            hours=email_config.email_link_expiration
        )
        mock_timezone.now.assert_called_once()
        token.delete.assert_called_once()
        user.delete.assert_not_called()
        mock_token.objects.create.assert_called_once_with(user=user)
        user.save.assert_called_once()
        mock_response.assert_called_once_with(status=204)
        assert user.is_verified is True
        assert result == mock_response.return_value
