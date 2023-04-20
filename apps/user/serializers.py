from django.contrib.auth.hashers import check_password
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from apps.service.models import ServiceModel
from apps.user.models import UserModel
from pipelines.pipes.user import CreateUserPipeline
from utils.messages import LOGIN_ERROR, NO_VERIFIED_USER


class CreateUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField(read_only=True)
    service = serializers.SlugRelatedField(
        slug_field="slug", queryset=ServiceModel.objects.all()
    )

    class Meta:
        model = UserModel
        fields = [
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

        extra_kwargs = {
            "password": {"write_only": True},
            "is_verified": {"read_only": True},
            "is_premium": {"read_only": True},
            "country": {"read_only": True},
            "date_joined": {"read_only": True},
        }

    @staticmethod
    def _validate_password(data):
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError(
                {"password": _("The passwords doesn't match.")}
            )

    @staticmethod
    def _validate_duplicated_email(data):
        email = data.get("email")
        service = data.get("service")

        try:
            UserModel.objects.get(email=email, service=service)
            raise ValidationError(
                {"user": _("A user with this email already exists.")}
            )
        except UserModel.DoesNotExist:
            pass

    @staticmethod
    def _validate_document(data, service):
        document = data.get("document")

        if document:
            try:
                UserModel.objects.get(
                    document=data.get("document"), service=service
                )

                raise ValidationError(
                    {
                        "document": _(
                            "A user with this document already exists."
                        )
                    }
                )
            except UserModel.DoesNotExist:
                pass

    def validate(self, data):
        service = data.get("service")
        request = self.context["request"]
        service.validate_credential_fields(request.data, "register")

        self._validate_password(data)
        self._validate_duplicated_email(data)
        self._validate_document(request.data, service)
        return data

    def get_token(self, obj):
        user = UserModel.objects.get(
            email=obj.get("email"), service=obj.get("service")
        )

        return Token.objects.get(user=user).key

    def save(self):
        request = self.context["request"]
        validated_data = self.validated_data
        service = ServiceModel.objects.get(slug=validated_data["service"])

        del validated_data["confirm_password"]

        validated_data["service"] = service
        credential_configs = service.credential_configs.filter(
            credential_config_type="register"
        ).exclude(field__in=["email", "password", "confirm_password"])

        for config in credential_configs.iterator():
            field = config.field
            validated_data[field] = request.data.get(field)

        pipeline = CreateUserPipeline(**validated_data)
        pipeline.run()


class UserDataSerializer(serializers.ModelSerializer):
    service = serializers.SlugRelatedField(
        slug_field="slug", queryset=ServiceModel.objects.all()
    )

    class Meta:
        model = UserModel
        fields = [
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

        extra_kwargs = {
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


class LoginSerializer(serializers.Serializer):
    user = None

    service = serializers.SlugRelatedField(
        slug_field="slug", queryset=ServiceModel.objects.all()
    )
    email = serializers.CharField()
    password = serializers.CharField()

    @staticmethod
    def _validate_password(password, password_to_check):
        is_valid_password = check_password(password, password_to_check)

        if not is_valid_password:
            raise UserModel.DoesNotExist

    @staticmethod
    def _validate_verified_user(user):
        login_was_blocked_by_service = (
            user.service.confirmation_required and not user.is_verified
        )

        if login_was_blocked_by_service:
            raise ValidationError(NO_VERIFIED_USER)

    @staticmethod
    def _validate_extra_fields(data, service):
        credential_configs = (
            service.credential_configs.only("field")
            .filter(credential_config_type="login")
            .exclude(field__in=["email", "password"])
        )

        for config in credential_configs.iterator():
            field = config.field
            email = data.get("email")

            query = {
                field: data.get(field),
                "service_id": service.id,
                "email": email,
            }

            UserModel.objects.get(**query)

    def validate(self, data):
        request = self.context["request"]
        service = data.get("service")
        email = data.get("email")
        password = data.get("password")

        service.validate_credential_fields(request.data, "login")

        try:
            user = (
                UserModel.objects.select_related("service")
                .only(
                    "password", "is_verified", "service__confirmation_required"
                )
                .get(email=email, service=service)
            )

            self._validate_password(password, user.password)
            self._validate_verified_user(user)
            self._validate_extra_fields(request.data, service)

            self.user = user

        except UserModel.DoesNotExist:
            raise ValidationError(LOGIN_ERROR)

        return data


class AuthenticatedUserSerializer(CreateUserSerializer):
    def get_token(self, user):
        return Token.objects.get_or_create(user=user)[0].key


class UserForRetentionSerializer(serializers.Serializer):
    delete_reason = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"[^*$ ]{2,} [^*$ ]{2,} [^*$ ]{2,}",
                message={
                    "delete_reason": (
                        "Is not format valid. More than three words and "
                        "each word with more than one letter."
                    )
                },
            )
        ]
    )
