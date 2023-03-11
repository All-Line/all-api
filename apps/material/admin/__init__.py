__all__ = [
    "CourseCategoryAdmin",
    "CourseAdmin",
    "LessonAdmin",
    "CommentAdmin",
    "LessonInline",
    "CommentInline",
    "LiveAdmin",
]

from apps.material.admin.courses import (
    CommentAdmin,
    CommentInline,
    CourseAdmin,
    CourseCategoryAdmin,
    LessonAdmin,
    LessonInline,
)
from apps.material.admin.lives import LiveAdmin
