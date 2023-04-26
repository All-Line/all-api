from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.buying.urls import *  # noqa
from apps.material.urls import *  # noqa
from apps.service.urls import *  # noqa
from apps.social.urls import *  # noqa
from apps.user.urls import *  # noqa


class PingViewAPI(APIView):
    @swagger_auto_schema(operation_summary="PingPong View")
    def get(self, _):
        return Response("pong")


admin.site.site_header = "All Line System"
admin.site.site_title = "All Line System"
admin.site.index_title = "All Line System"

schema_view = get_schema_view(
    openapi.Info(
        title="All Line System API Gateway",
        default_version="v1",
        description=_("This is the All Line system API layer documentation."),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("api/v1/ping/", PingViewAPI.as_view()),
    path("api/v1/docs/", schema_view.with_ui("redoc", cache_timeout=0)),
    path("api/v1/", include(router.urls)),  # noqa: F405
    path("admin/", admin.site.urls),
]
