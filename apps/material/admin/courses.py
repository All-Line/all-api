from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.material.models import (
    CommentModel,
    CourseCategoryModel,
    CourseModel,
    LessonModel,
)
from utils.admin import admin_method_attributes


@admin.register(CourseCategoryModel)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title_style", "description", "date_modified"]
    search_fields = ["title"]
    readonly_fields = ["id", "date_modified"]
    fieldsets = ((_("Identification"), {"fields": ("title", "description", "color")}),)

    @admin_method_attributes(short_description=_("Title"))
    def title_style(self, category):
        category_color = getattr(category, "color")
        color = getattr(category_color, "color", "#06D6A0")
        category_title = category.title

        return (
            "<div style='background-color: #333333; display: inline-block; "
            f"padding: 5px 20px; color: {color}; "
            f"border: 2px outset {color}; "
            f"border-radius: 10px;'>{category_title}</div>"
        )


class LessonInline(admin.TabularInline):
    model = LessonModel
    verbose_name_plural = _("Lessons")
    extra = 0
    fields = (
        "title",
        "description",
        "thumbnail",
        "order",
        "lesson_type",
        "likes_amount",
    )
    readonly_fields = [
        "title",
        "description",
        "thumbnail",
        "lesson_type",
        "likes_amount",
    ]

    def has_add_permission(self, request, obj):
        return False


@admin.register(CourseModel)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "description",
        "is_paid",
        "color_palette",
        "course_mode",
    ]
    inlines = [LessonInline]
    search_fields = ["title", "slug"]
    list_filter = ["is_paid", "service__name", "course_mode", "categories"]
    filter_horizontal = ["categories"]
    readonly_fields = ["id"]
    fieldsets = (
        (
            _("Identification"),
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
        ),
        (_("Settings"), {"fields": ("service", "categories", "color_palette")}),
    )


class CommentInline(admin.TabularInline):
    model = CommentModel
    verbose_name_plural = _("Comments")
    extra = 0
    fields = ("text", "author")
    readonly_fields = ("text", "author")

    def has_add_permission(self, request, obj):
        return False


@admin.register(LessonModel)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "lesson_type",
        "description",
        "likes_amount",
        "total_comments",
        "course",
    ]
    readonly_fields = ["id"]
    inlines = [CommentInline]
    fieldsets = (
        (
            _("Identification"),
            {
                "fields": (
                    "title",
                    "description",
                    "lesson_type",
                    "thumbnail",
                )
            },
        ),
        (
            _("Settings"),
            {
                "fields": (
                    "course",
                    "order",
                    "reading_time",
                    "text",
                    "video",
                    "audio",
                )
            },
        ),
        (
            _("Accessibility Fields"),
            {"fields": ("video_transcript", "audio_transcript")},
        ),
    )

    @staticmethod
    def total_comments(lesson):
        return mark_safe(f"<span>{lesson.comments.only('id').count()}</span>")


@admin.register(CommentModel)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "__str__", "date_joined"]
    readonly_fields = ["id", "text", "lesson", "author"]
    list_filter = ["author", "lesson__title"]
    search_fields = ["text"]
    fieldsets = (("Identification", {"fields": ("text", "lesson", "author")}),)

    def has_add_permission(self, request):
        return False
