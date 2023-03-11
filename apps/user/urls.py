from utils import router

from .views import UserViewSet

app_name = "apps.user"

router.register("user", UserViewSet, basename="user")
