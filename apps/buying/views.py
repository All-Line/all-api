from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from apps.buying.models import ContractModel, PackageModel
from apps.buying.serializers import CreateContractSerializer, PackageSerializer
from utils.auth import BearerTokenAuthentication
from utils.mixins.service_context import ReadWithServiceContextMixin


class PackageViewSet(ReadWithServiceContextMixin, ReadOnlyModelViewSet):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PackageModel.objects.only("id", "is_active", "price", "slug").filter(
        is_active=True
    )
    serializer_class = PackageSerializer
    lookup_field = "slug"

    @swagger_auto_schema(operation_summary=_("Package Detail"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Packages"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ContractViewSet(GenericViewSet, mixins.CreateModelMixin):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CreateContractSerializer
    queryset = ContractModel.objects.only("id").all()

    @swagger_auto_schema(operation_summary=_("Create Contract"))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
