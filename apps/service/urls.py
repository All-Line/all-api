from utils import router

from .views import ServiceViewSet

app_name = "apps.service"

router.register(r"service", ServiceViewSet, basename="service")
