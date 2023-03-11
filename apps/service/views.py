from django.http import Http404
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.mixins.multiserializer import MultiSerializerMixin

from .models import ServiceModel
from .serializers import (
    RetrieveServiceSerializer,
    ServiceCredentialConfigSerializer,
    TermsServiceSerializer,
)


class ServiceViewSet(MultiSerializerMixin, GenericViewSet, mixins.RetrieveModelMixin):
    queryset = (
        ServiceModel.objects.prefetch_related("colors_palettes")
        .only(
            "id",
            "is_active",
            "name",
            "slug",
            "url",
            "confirmation_required",
            "language",
            "terms",
        )
        .filter(is_active=True)
    )
    serializers = {
        "retrieve": RetrieveServiceSerializer,
        "terms": TermsServiceSerializer,
        "credential_fields": ServiceCredentialConfigSerializer,
    }
    lookup_field = "slug"

    @swagger_auto_schema(operation_summary=_("Service Detail"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Service Terms and Conditions"))
    @action(detail=True, methods=["get"])
    def terms(self, _, *args, **kwargs):
        service = self.get_object()

        return Response({"terms": service.terms})

    @swagger_auto_schema(operation_summary=_("Service Terms and Conditions"))
    @action(
        detail=True,
        methods=["get"],
        url_path=r"credential-fields/(?P<credential_config_type>[^/.]+)",
    )
    def credential_fields(self, _, credential_config_type, *args, **kwargs):
        valid_credential_config_type = ["register", "login"]

        if credential_config_type not in valid_credential_config_type:
            raise Http404

        service = self.get_object()
        configs = service.credential_configs.only(
            "id",
            "credential_config_type",
            "field",
            "label",
            "field_html_type",
            "rule",
            "no_match_message",
        ).filter(credential_config_type=credential_config_type, is_active=True)

        serializer = self.get_serializer(configs, many=True)

        return Response(serializer.data)
