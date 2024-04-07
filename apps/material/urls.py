from utils import router

from .views import CourseViewSet, LiveViewSet

app_name = "apps.material"

router.register(r"course", CourseViewSet)
router.register(r"live", LiveViewSet)
