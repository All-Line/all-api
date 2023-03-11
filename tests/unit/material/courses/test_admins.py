from unittest.mock import Mock, call, patch

from django.contrib import admin
from django.contrib.admin import AdminSite

from apps.material.admin import (
    CommentAdmin,
    CommentInline,
    CourseAdmin,
    CourseCategoryAdmin,
    LessonAdmin,
    LessonInline,
)
from apps.material.models import (
    CommentModel,
    CourseCategoryModel,
    CourseModel,
    LessonModel,
)


class TestCourseCategoryAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = CourseCategoryAdmin(CourseCategoryModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == CourseCategoryModel

    def test_admin_subclass(self):
        assert issubclass(CourseCategoryAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "title_style",
            "description",
            "date_modified",
        ]

    def test_search_fields(self):
        assert self.admin.search_fields == ["title"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id", "date_modified"]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
            {"fields": ("title", "description", "color")},
        )

    @patch("apps.material.admin.courses.getattr")
    def test_title_style(self, mock_getattr):
        mock_category = Mock()
        result = self.admin.title_style(mock_category)

        assert mock_getattr.call_args_list == [
            call(mock_category, "color"),
            call(mock_getattr.return_value, "color", "#06D6A0"),
        ]
        assert result == (
            "<div style='background-color: #333333; display: inline-block; "
            f"padding: 5px 20px; color: {mock_getattr.return_value}; "
            f"border: 2px outset {mock_getattr.return_value}; "
            f"border-radius: 10px;'>{mock_category.title}</div>"
        )


class TestLessonInline:
    @classmethod
    def setup_class(cls):
        cls.inline = LessonInline(LessonModel, AdminSite())

    def test_meta_model(self):
        assert self.inline.model == LessonModel

    def test_admin_subclass(self):
        assert issubclass(LessonInline, admin.TabularInline)

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Lessons"

    def test_extra_field(self):
        assert self.inline.extra == 0

    def test_inline_fields(self):
        assert self.inline.fields == (
            "title",
            "description",
            "thumbnail",
            "order",
            "lesson_type",
            "likes_amount",
        )

    def test_readonly_fields(self):
        assert self.inline.readonly_fields == [
            "title",
            "description",
            "thumbnail",
            "lesson_type",
            "likes_amount",
        ]

    def test_has_add_permission(self):
        result = self.inline.has_add_permission(None, None)

        assert result is False


class TestCourseAdmin:
    @classmethod
    def setup_class(cls):
        cls.inline = CourseAdmin(CourseModel, AdminSite())

    def test_meta_model(self):
        assert self.inline.model == CourseModel

    def test_admin_subclass(self):
        assert issubclass(CourseAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.inline.list_display == [
            "id",
            "title",
            "description",
            "is_paid",
            "color_palette",
            "course_mode",
        ]

    def test_inlines_model(self):
        assert self.inline.inlines == [LessonInline]

    def test_search_fields(self):
        assert self.inline.search_fields == ["title", "slug"]

    def test_list_filter(self):
        assert self.inline.list_filter == [
            "is_paid",
            "service__name",
            "course_mode",
            "categories",
        ]

    def test_filter_horizontal(self):
        assert self.inline.filter_horizontal == ["categories"]

    def test_readonly_fields(self):
        assert self.inline.readonly_fields == ["id"]

    def test_fieldsets_identification(self):
        assert self.inline.fieldsets[0] == (
            "Identification",
            {
                "fields": (
                    "title",
                    "description",
                    "image",
                    "trailer",
                    "is_paid",
                    "slug",
                    "course_mode",
                )
            },
        )

    def test_fieldsets_relationship(self):
        assert self.inline.fieldsets[1] == (
            "Settings",
            {"fields": ("service", "categories", "color_palette")},
        )


class TestCommentInlineAdmin:
    @classmethod
    def setup_class(cls):
        cls.inline = CommentInline(CommentModel, AdminSite())

    def test_meta_model(self):
        assert self.inline.model == CommentModel

    def test_admin_subclass(self):
        assert issubclass(CommentInline, admin.TabularInline)

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Comments"

    def test_extra(self):
        assert self.inline.extra == 0

    def test_fields(self):
        assert self.inline.fields == ("text", "author")

    def test_readonly_fields(self):
        assert self.inline.readonly_fields == ("text", "author")

    def test_has_add_permission(self):
        result = self.inline.has_add_permission(None, None)

        assert result is False


class TestLessonAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = LessonAdmin(LessonModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == LessonModel

    def test_admin_subclass(self):
        assert issubclass(LessonAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "title",
            "lesson_type",
            "description",
            "likes_amount",
            "total_comments",
            "course",
        ]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id"]

    def test_inlines(self):
        assert self.admin.inlines == [CommentInline]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
            {
                "fields": (
                    "title",
                    "description",
                    "lesson_type",
                    "thumbnail",
                )
            },
        )

    def test_fieldsets_settings(self):
        assert self.admin.fieldsets[1] == (
            "Settings",
            {"fields": ("course", "order", "reading_time", "text", "video", "audio")},
        )

    def test_fieldsets_accessibility_fields(self):
        assert self.admin.fieldsets[2] == (
            "Accessibility Fields",
            {
                "fields": (
                    "video_transcript",
                    "audio_transcript",
                )
            },
        )

    @patch("apps.material.admin.courses.mark_safe")
    def test_total_comments(self, mock_mark_safe):
        mock_lesson = Mock()
        mock_lesson.comments.only.return_value.count.return_value = 3
        result = self.admin.total_comments(mock_lesson)

        mock_mark_safe.assert_called_once_with("<span>3</span>")
        mock_lesson.comments.only.assert_called_once_with("id")
        mock_lesson.comments.only.return_value.count.assert_called_once()

        assert result == mock_mark_safe.return_value


class TestCommentAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = CommentAdmin(CommentModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == CommentModel

    def test_admin_subclass(self):
        assert issubclass(CommentAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == ["id", "__str__", "date_joined"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id", "text", "lesson", "author"]

    def test_list_filter(self):
        assert self.admin.list_filter == ["author", "lesson__title"]

    def test_search_fields(self):
        assert self.admin.search_fields == ["text"]

    def test_fieldsets_settings(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
            {"fields": ("text", "lesson", "author")},
        )

    def test_has_add_permission(self):
        result = self.admin.has_add_permission(None)

        assert result is False
