from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.material.models import CourseModel
from apps.material.serializers import CourseSerializer
from utils.auth import BearerTokenAuthentication
from utils.exceptions.http import HttpPaymentRequired
from utils.mixins.service_context import ReadWithServiceContextMixin


class CourseViewSet(ReadWithServiceContextMixin, ReadOnlyModelViewSet):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer
    queryset = (
        CourseModel.objects.select_related("color_palette", "service")
        .prefetch_related("lessons", "categories")
        .only(
            "id",
            "is_active",
            "title",
            "description",
            "image",
            "trailer",
            "is_paid",
            "slug",
            "course_mode",
            "service",
            "color_palette",
        )
        .filter(is_active=True)
    )
    lookup_field = "slug"

    @swagger_auto_schema(operation_summary=_("Course Detail"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Courses"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if not user.can_access(obj):
            raise HttpPaymentRequired

        return obj
