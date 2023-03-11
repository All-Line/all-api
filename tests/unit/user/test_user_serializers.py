from unittest.mock import Mock, call, patch

import pytest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.user.models import UserModel
from apps.user.serializers import (
    AuthenticatedUserSerializer,
    CreateUserSerializer,
    LoginSerializer,
    UserDataSerializer,
    UserForRetentionSerializer,
)


class TestCreateUserSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = CreateUserSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == UserModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "token",
            "service",
            "is_verified",
            "is_premium",
            "birth_date",
            "country",
            "date_joined",
        ]

    def test_meta_extra_kwargs(self):
        assert self.serializer.Meta.extra_kwargs == {
            "password": {"write_only": True},
            "is_verified": {"read_only": True},
            "is_premium": {"read_only": True},
            "country": {"read_only": True},
            "date_joined": {"read_only": True},
        }

    def test_validate_password_failure(self):
        data = {
            "password": "some_password",
            "confirm_password": "some_confirm_password",
        }

        with pytest.raises(ValidationError) as err:
            self.serializer._validate_password(data)

        assert err.value.detail == {"password": "The passwords doesn't match."}

    @patch("apps.user.serializers.UserModel")
    def test_validate_duplicated_email_successfully(self, mock_user_model):
        data = {
            "email": "some_email",
            "service": "some_service",
        }
        mock_user_model.DoesNotExist = Exception
        mock_user_model.objects.get.side_effect = Exception()
        self.serializer._validate_duplicated_email(data)

        mock_user_model.objects.get.assert_called_once_with(**data)

    @patch("apps.user.serializers.UserModel")
    def test_validate_duplicated_email_failure(self, mock_user_model):
        data = {
            "email": "some_email",
            "service": "some_service",
        }
        mock_user_model.DoesNotExist = UserModel.DoesNotExist

        with pytest.raises(ValidationError) as err:
            self.serializer._validate_duplicated_email(data)

        mock_user_model.objects.get.assert_called_once_with(**data)
        assert err.value.detail == {"user": "A user with this email already exists."}

    @patch("apps.user.serializers.UserModel")
    def test_validate_document_failure_with_user_already_exists(self, mock_user_model):
        mock_user_model.DoesNotExist = UserModel.DoesNotExist
        data = {
            "email": "some_email",
            "service": "some_service",
            "document": "12312312312",
        }

        with pytest.raises(ValidationError) as err:
            self.serializer._validate_document(data, "some_service")

        mock_user_model.objects.get.assert_called_once_with(
            document=data["document"], service=data["service"]
        )
        assert err.value.detail == {
            "document": "A user with this document already exists."
        }

    @patch("apps.user.serializers.UserModel")
    def test_validate_document_without_document(self, mock_user_model):
        mock_user_model.DoesNotExist = UserModel.DoesNotExist
        data = {
            "email": "some_email",
            "service": "some_service",
        }

        result = self.serializer._validate_document(data, "some_service")

        mock_user_model.objects.get.assert_not_called()

        assert result is None

    @patch("apps.user.serializers.UserModel")
    def test_validate_successfully(self, mock_user_model):
        mock_user_model.DoesNotExist = UserModel.DoesNotExist
        mock_user_model.objects.get.side_effect = UserModel.DoesNotExist()
        mock_user_model.objects.get.return_value = "user"
        data = {
            "email": "some_email",
            "service": "some_service",
            "document": "12312312312",
        }

        self.serializer._validate_document(data, "some_service")

        mock_user_model.objects.get.assert_called_once_with(
            document=data["document"], service=data["service"]
        )

    def test_validate(self):
        data = {"service": Mock()}
        context = {"request": Mock()}
        mock_self = Mock(context=context)
        response = self.serializer.validate(mock_self, data)

        mock_self._validate_password.assert_called_once_with(data)
        mock_self._validate_duplicated_email.assert_called_once_with(data)
        assert response == data

    @patch("apps.user.serializers.UserModel")
    @patch("apps.user.serializers.Token")
    def test_get_token(self, mock_token, mock_user_model):
        obj = {"email": "some_email@email.com", "service": "some_service"}
        response = self.serializer().get_token(obj)

        mock_user_model.objects.get.assert_called_once_with(
            email="some_email@email.com",
            service="some_service",
        )
        mock_token.objects.get.assert_called_once_with(
            user=mock_user_model.objects.get.return_value
        )
        assert response == mock_token.objects.get.return_value.key

    @patch("apps.user.serializers.CreateUserPipeline")
    @patch("apps.user.serializers.ServiceModel")
    def test_save(self, mock_service_model, mock_create_user_pipeline):
        mock_config = Mock(field="foo")
        service = mock_service_model.objects.get.return_value
        filtered_configs = service.credential_configs.filter.return_value
        exclude_config = filtered_configs.exclude.return_value
        exclude_config.iterator.return_value = [mock_config]
        request = Mock()
        request.data.get.return_value = "bar"
        serializer = self.serializer(context={"request": request})
        validated_data = {
            "confirm_password": "some_confirm_password",
            "service": "some_service",
        }
        serializer._validated_data = validated_data
        serializer.save()

        service = mock_service_model.objects.get.return_value
        credential_configs = service.credential_configs.filter.return_value

        mock_service_model.objects.get.assert_called_once_with(slug="some_service")
        service.credential_configs.filter.assert_called_once_with(
            credential_config_type="register"
        )
        credential_configs.exclude.assert_called_once_with(
            field__in=["email", "password", "confirm_password"]
        )
        mock_create_user_pipeline.assert_called_once_with(**validated_data)
        mock_create_user_pipeline.return_value.run.assert_called_once()
        assert validated_data == {
            "foo": "bar",
            "service": mock_service_model.objects.get.return_value,
        }


class TestUserDataSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = UserDataSerializer

    def test_parent_class(self):
        assert issubclass(self.serializer, serializers.ModelSerializer)

    def test_meta_model(self):
        assert self.serializer.Meta.model == UserModel

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "first_name",
            "last_name",
            "profile_image",
            "username",
            "service",
            "is_verified",
            "is_premium",
            "birth_date",
            "country",
            "date_joined",
        ]

    def test_meta_extra_kwargs(self):
        assert self.serializer.Meta.extra_kwargs == {
            "service": {
                "read_only": True,
            },
            "is_verified": {
                "read_only": True,
            },
            "is_premium": {
                "read_only": True,
            },
            "date_joined": {
                "read_only": True,
            },
        }


class TestLoginSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = LoginSerializer

    def test_parent_class(self):
        assert issubclass(LoginSerializer, serializers.Serializer)

    @patch("apps.user.serializers.check_password")
    def test_validate_password(self, mock_check_password):
        mock_check_password.return_value = False

        password = "foo"
        password_to_check = "bar"

        with pytest.raises(UserModel.DoesNotExist):
            self.serializer._validate_password(password, password_to_check)

        mock_check_password.assert_called_once_with(password, password_to_check)

    def test_validate_verified_user(self):
        blocked_user = Mock(is_verified=False, service=Mock(confirmation_required=True))

        with pytest.raises(ValidationError):
            self.serializer._validate_verified_user(blocked_user)

    @patch("apps.user.serializers.UserModel")
    def test_validate_extra_fields(self, mock_user_model):
        mock_data = {"foo": "bar"}
        config_1 = Mock(field="foo")
        config_2 = Mock(field="foo")
        mock_service = Mock()
        filtered_configs = (
            mock_service.credential_configs.only.return_value.filter.return_value
        )
        exclude_configs = filtered_configs.exclude.return_value
        exclude_configs.iterator.return_value = [
            config_1,
            config_2,
        ]

        self.serializer._validate_extra_fields(mock_data, mock_service)

        credential_configs = (
            mock_service.credential_configs.only.return_value.filter.return_value
        )
        mock_service.credential_configs.only.assert_called_once_with("field")
        mock_service.credential_configs.only.return_value.filter.assert_called_once_with(  # noqa: E501
            credential_config_type="login"
        )
        credential_configs.exclude.assert_called_once_with(
            field__in=["email", "password"]
        )
        credential_configs.exclude.return_value.iterator.assert_called_once()
        assert mock_user_model.objects.get.call_args_list == [
            call(foo="bar", service_id=mock_service.id, email=None),
            call(foo="bar", service_id=mock_service.id, email=None),
        ]

    @patch("apps.user.serializers.UserModel")
    def test_validate_failure_with_user_does_not_exist(
        self,
        mock_user_model,
    ):
        mock_user_model.DoesNotExist = UserModel.DoesNotExist
        mock_user_model.objects.select_related.return_value.only.return_value.get.side_effect = (  # noqa: E501
            UserModel.DoesNotExist()
        )
        mock_service = Mock()
        context = {"request": Mock()}
        mock_self = Mock(context=context)
        data = {
            "service": mock_service,
            "email": "dummy@mail.com",
            "password": "Dummy123!",
        }

        with pytest.raises(ValidationError):
            self.serializer.validate(mock_self, data)

        mock_service.validate_credential_fields.assert_called_once_with(
            mock_self.context["request"].data, "login"
        )
        mock_user_model.objects.select_related.assert_called_once_with("service")
        mock_user_model.objects.select_related.return_value.only.assert_called_once_with(  # noqa: E501
            "password", "is_verified", "service__confirmation_required"
        )
        mock_user_model.objects.select_related.return_value.only.return_value.get.assert_called_once_with(  # noqa: E501
            email="dummy@mail.com", service=mock_service
        )

    @patch("apps.user.serializers.UserModel")
    def test_validate_successfully(self, mock_user_model):
        mock_user_model.DoesNotExist = UserModel.DoesNotExist
        mock_service = Mock()
        context = {"request": Mock()}
        mock_self = Mock(context=context)
        data = {
            "service": mock_service,
            "email": "dummy@mail.com",
            "password": "Dummy123!",
        }

        response = self.serializer.validate(mock_self, data)

        mock_service.validate_credential_fields.assert_called_once_with(
            mock_self.context["request"].data, "login"
        )
        mock_user_model.objects.select_related.assert_called_once_with("service")
        mock_user_model.objects.select_related.return_value.only.assert_called_once_with(  # noqa: E501
            "password", "is_verified", "service__confirmation_required"
        )
        mock_user_model.objects.select_related.return_value.only.return_value.get.assert_called_once_with(  # noqa: E501
            email="dummy@mail.com", service=mock_service
        )
        mock_self._validate_password.assert_called_once_with(
            "Dummy123!",
            mock_user_model.objects.select_related.return_value.only.return_value.get.return_value.password,  # noqa: E501
        )
        mock_self._validate_verified_user.assert_called_once_with(
            mock_user_model.objects.select_related.return_value.only.return_value.get.return_value  # noqa: E501
        )
        mock_self._validate_extra_fields.assert_called_once_with(
            mock_self.context["request"].data, mock_service
        )

        assert response == data


class TestAuthenticatedUserSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = AuthenticatedUserSerializer()

    def test_parent_class(self):
        assert issubclass(AuthenticatedUserSerializer, CreateUserSerializer)

    def test_get_token(self):
        user = Mock()
        response = self.serializer.get_token(user)

        assert response == str(user.auth_token)


class TestUserForRetentionSerializer:
    def test_parent_class(self):
        assert issubclass(UserForRetentionSerializer, serializers.Serializer)
