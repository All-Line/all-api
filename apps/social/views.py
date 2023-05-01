from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.auth import BearerTokenAuthentication
from utils.mixins.multiserializer import MultiSerializerMixin

from .models import LoginQuestions, MissionModel, PostModel, ReactionTypeModel
from .serializers import (
    AnswerLoginQuestionSerializer,
    CompleteMissionSerializer,
    CreatePostCommentSerializer,
    CreateReactionSerializer,
    ListMissionSerializer,
    ListPostCommentSerializer,
    ListPostSerializer,
    ListReactTypesSerializer,
    LoginQuestionSerializer,
    UnreactSerializer,
)


class ServiceAndEventContextMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_guest = user.is_guest
        filter_by = {"service_id": user.service_id}

        if is_guest:
            filter_by["event_id"] = user.event_id

        return queryset.filter(**filter_by)


class PostViewSet(
    ServiceAndEventContextMixin,
    MultiSerializerMixin,
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = (
        PostModel.objects.prefetch_related("reactions")
        .select_related("service", "event", "author")
        .filter(is_active=True)
    )
    serializers = {
        "list": ListPostSerializer,
        "retrieve": ListPostSerializer,
        "comment": CreatePostCommentSerializer,
        "react": CreateReactionSerializer,
        "unreact": UnreactSerializer,
        "react_types": ListReactTypesSerializer,
    }

    @swagger_auto_schema(operation_summary=_("Post List"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Post Detail"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Comment to post"))
    @action(detail=False, methods=["post"])
    def comment(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        response = ListPostCommentSerializer(comment).data

        return Response(response)

    @swagger_auto_schema(operation_summary=_("React to post"))
    @action(detail=False, methods=["post"])
    def react(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_summary=_("Remove reaction"))
    @action(detail=False, methods=["post"])
    def unreact(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_summary=_("Get reaction types"))
    @action(detail=False, methods=["get"], url_path="react-types")
    def react_types(self, request):
        user = request.user
        queryset = ReactionTypeModel.objects.filter(
            service_id=user.service_id,
        )
        serializer = self.get_serializer(queryset, many=True)
        response = serializer.data

        return Response(response)


class MissionViewSet(
    ServiceAndEventContextMixin,
    MultiSerializerMixin,
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    queryset = MissionModel.objects.prefetch_related("interactions").all()
    serializers = {
        "list": ListMissionSerializer,
        "retrieve": ListMissionSerializer,
        "complete": CompleteMissionSerializer,
    }
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary=_("Mission List"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Mission Detail"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Complete Mission"))
    @action(detail=False, methods=["post"])
    def complete(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginQuestionViewSet(
    MultiSerializerMixin,
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    queryset = (
        LoginQuestions.objects.prefetch_related("options").order_by("order").all()
    )
    serializers = {
        "list": LoginQuestionSerializer,
        "retrieve": LoginQuestionSerializer,
        "answer": AnswerLoginQuestionSerializer,
    }
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_guest = user.is_guest
        filter_by = {"event_id": user.event_id}

        if not is_guest:
            raise ValidationError(
                {"error": _("Only guests can answer login questions")}
            )

        queryset = queryset.filter(**filter_by)

        without_answered_questions = queryset.exclude(
            answers__user_id=user.id,
        )

        return without_answered_questions

    @swagger_auto_schema(operation_summary=_("Login Question List"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Login Question Detail"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Answer Login Question"))
    @action(detail=False, methods=["post"])
    def answer(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
