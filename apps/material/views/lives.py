from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.material.models import LiveModel
from apps.material.serializers import LiveSerializer
from utils.auth import BearerTokenAuthentication
from utils.mixins.service_context import ListObjectServiceContextMixin


class LiveViewSet(ListObjectServiceContextMixin, GenericViewSet, ListModelMixin):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LiveSerializer
    queryset = (
        LiveModel.objects.select_related("service")
        .only(
            "id",
            "title",
            "description",
            "slug",
            "is_paid",
            "starts_at",
            "integration_field",
            "live_type",
            "image",
            "service",
        )
        .filter(is_active=True, starts_at__date__gte=timezone.now().date())
        .order_by("starts_at")
    )

    @swagger_auto_schema(operation_summary=_("Live Calendar"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
