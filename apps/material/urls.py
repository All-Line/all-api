from utils import router

from .views import CourseViewSet, LiveViewSet

app_name = "apps.material"

router.register(r"course", CourseViewSet, basename="course")
router.register(r"live", LiveViewSet, basename="course")
