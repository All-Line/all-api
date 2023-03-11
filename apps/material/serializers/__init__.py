__all__ = [
    "AuthorSerializer",
    "CommentSerializer",
    "LessonSerializer",
    "CourseCategorySerializer",
    "CourseSerializer",
    "LiveSerializer",
]

from apps.material.serializers.courses import (
    AuthorSerializer,
    CommentSerializer,
    CourseCategorySerializer,
    CourseSerializer,
    LessonSerializer,
)
from apps.material.serializers.lives import LiveSerializer
