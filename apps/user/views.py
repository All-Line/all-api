from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.user.models import UserModel
from apps.user.permissions import UserPermissions
from apps.user.serializers import (
    AuthenticatedUserSerializer,
    CreateUserSerializer,
    LoginSerializer,
    UserDataSerializer,
    UserForRetentionSerializer,
)
from utils.auth import BearerTokenAuthentication
from utils.mixins.multiserializer import MultiSerializerMixin


class UserViewSet(MultiSerializerMixin, GenericViewSet, mixins.CreateModelMixin):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [UserPermissions]
    serializers = {
        "create": CreateUserSerializer,
        "me": UserDataSerializer,
        "update_me": UserDataSerializer,
        "login": LoginSerializer,
        "delete_me": UserForRetentionSerializer,
    }
    queryset = UserModel.objects.all()

    @swagger_auto_schema(operation_summary=_("Registration"))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Get my data"))
    @action(detail=False, methods=["get"])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    @swagger_auto_schema(operation_summary=_("Update my data"))
    @action(detail=False, methods=["patch"])
    def update_me(self, request):
        user = request.user

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    @swagger_auto_schema(operation_summary=_("Login"))
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        user_data = AuthenticatedUserSerializer(user).data

        return Response(user_data)

    @swagger_auto_schema(operation_summary=_("Start retention proccess"))
    @action(detail=False, methods=["delete"])
    def delete_me(self, request):
        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.delete_reason = request.data["delete_reason"]
        user.is_deleted = True
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_summary=_("Confirm Email"))
    @action(detail=False, url_path="confirm_email/(?P<token>.+)", methods=["get"])
    def confirm_email(self, request, token):
        try:
            token = (
                Token.objects.select_related("user")
                .only("user", "created")
                .get(key=token)
            )
        except Token.DoesNotExist:
            return Response(
                {"detail": _("This link is expired")}, status=status.HTTP_410_GONE
            )

        user = token.user
        service = user.service

        email_config = (
            service.email_configs.only("email_link_expiration")
            .filter(email_config_type="register")
            .first()
        )
        link_expiration = timedelta(
            hours=getattr(email_config, "email_link_expiration", 1)
        )

        expiration_time = token.created + link_expiration

        is_expired = timezone.now() > expiration_time

        if is_expired:
            token.delete()
            user.delete()

            return Response(
                {"detail": _("This link is expired")}, status=status.HTTP_410_GONE
            )

        token.delete()
        Token.objects.create(user=user)
        user.is_verified = True
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
