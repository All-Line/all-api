from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.auth import BearerTokenAuthentication
from utils.mixins.multiserializer import MultiSerializerMixin

from .models import PostModel, ReactionTypeModel
from .permissions import PostPermissions
from .serializers import (
    CreatePostCommentSerializer,
    CreateReactionSerializer,
    ListPostCommentSerializer,
    ListPostSerializer,
    ListReactTypesSerializer,
    UnreactSerializer,
)


class PostViewSet(
    MultiSerializerMixin,
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [PostPermissions]
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

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_guest = user.is_guest
        filter_by = {"service_id": user.service_id}

        if is_guest:
            filter_by["event_id"] = user.event_id

        return queryset.filter(**filter_by)

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
