from utils import router

from .views import GuestViewSet, LoginQuestionViewSet, MissionViewSet, PostViewSet

app_name = "apps.social"

router.register(r"post", PostViewSet, basename="post")
router.register(r"mission", MissionViewSet, basename="mission")
router.register(r"login-question", LoginQuestionViewSet, basename="login-question")
router.register(r"event", GuestViewSet, basename="event")
