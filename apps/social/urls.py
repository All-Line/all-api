from utils import router

from .views import PostViewSet

app_name = "apps.social"

router.register(r"post", PostViewSet, basename="post")
