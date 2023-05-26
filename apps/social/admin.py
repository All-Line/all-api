from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.service.admin import ServiceEmailConfigInline
from apps.social.models import (
    AITextReportModel,
    EventModel,
    LoginAnswer,
    LoginQuestionOption,
    LoginQuestions,
    MissionInteractionModel,
    MissionModel,
    MissionTypeModel,
    PostCommentModel,
    PostModel,
)
from utils.admin import admin_method_attributes
from utils.admin.mixins import (
    AttachmentPreviewMixin,
    UpdateDateModifiedMixin,
    UpdateDateModifiedOrSetAuthorMixin,
)


@admin.register(AITextReportModel)
class AITextReportAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "text_ai", "is_active"]
    readonly_fields = ["id"]
    list_filter = [
        "is_active",
    ]
    search_fields = ["text_ai"]
    fieldsets = (
        (
            _("Text AI Config"),
            {"fields": ("id", "title", "pre_set", "text_ai", "is_active")},
        ),
    )


class PostCommentInline(admin.TabularInline):
    model = PostCommentModel
    verbose_name_plural = "Comments"
    extra = 0
    fields = (
        "id",
        "content",
        "author",
        "reactions_amount",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj):
        return False


@admin.register(PostModel)
class PostAdmin(
    UpdateDateModifiedOrSetAuthorMixin, AttachmentPreviewMixin, admin.ModelAdmin
):
    list_display = ["id", "author", "service", "reactions_amount", "attachment_preview"]
    readonly_fields = ["id", "author", "ai_report", "attachment_preview"]
    list_filter = [
        "service__name",
    ]
    search_fields = ["description", "author__first_name", "service__name"]
    inlines = [PostCommentInline]

    fieldsets = (
        (_("Post"), {"fields": ("description", "attachment", "attachment_preview")}),
        (
            _("AI Report"),
            {
                "fields": (
                    "ai_text_report",
                    "ai_report",
                )
            },
        ),
        (_("Config"), {"fields": ("author", "service", "event")}),
    )

    actions = ["generate_ai_report"]

    def generate_ai_report(self, _, queryset):
        for post in queryset:
            post.generate_ai_text_report()


@admin.register(PostCommentModel)
class PostCommentAdmin(UpdateDateModifiedOrSetAuthorMixin, admin.ModelAdmin):
    list_display = ["id", "author", "post", "reactions_amount", "is_deleted"]
    readonly_fields = ["id", "author"]
    list_filter = ["post__service__name", "author__first_name", "post"]
    search_fields = ["content", "author__first_name", "post__service__name"]

    fieldsets = (
        (_("Comment"), {"fields": ("content", "is_deleted")}),
        (_("Config"), {"fields": ("author", "post")}),
    )


class PostInline(admin.TabularInline, AttachmentPreviewMixin):
    model = PostModel
    verbose_name_plural = "Posts"
    extra = 0
    fields = (
        "id",
        "description",
        "attachment",
        "attachment_preview",
        "reactions_amount",
    )
    readonly_fields = fields


@admin.register(EventModel)
class EventAdmin(UpdateDateModifiedMixin, AttachmentPreviewMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "service",
        "event_type",
        "is_active",
        "attachment_preview",
    ]
    readonly_fields = ["id", "date_joined", "date_modified", "attachment_preview"]
    list_filter = [
        "service__name",
    ]
    search_fields = ["title", "service__name"]
    inlines = [ServiceEmailConfigInline, PostInline]

    fieldsets = (
        (
            _("Event"),
            {
                "fields": (
                    "title",
                    "description",
                    "event_type",
                    "attachment",
                    "attachment_preview",
                )
            },
        ),
        (
            _("Config"),
            {
                "fields": (
                    "smtp_email",
                    "guests",
                    "send_email_to_guests",
                    "require_login_answers",
                    "service",
                    "service_client",
                    "is_active",
                    "event_link",
                    "date_joined",
                    "date_modified",
                )
            },
        ),
    )
    actions = ["send_invite_to_guests"]

    def send_invite_to_guests(self, _, events):
        for event in events:
            event.create_guests()


class MissionInteractionInline(AttachmentPreviewMixin, admin.TabularInline):
    model = MissionInteractionModel
    verbose_name_plural = "Interactions"
    extra = 0
    fields = (
        "id",
        "mission",
        "user",
        "attachment",
        "attachment_preview",
        "content",
        "date_joined",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj):
        return False


@admin.register(MissionInteractionModel)
class MissionInteractionAdmin(admin.ModelAdmin, AttachmentPreviewMixin):
    list_display = [
        "id",
        "mission",
        "user",
        "date_joined",
        "attachment_preview",
        "is_active",
    ]
    readonly_fields = ["id", "mission", "user", "date_joined", "attachment_preview"]
    list_filter = [
        "mission__service__name",
        "mission__event__title",
        "mission__is_active",
        "mission",
    ]

    def has_add_permission(self, *_args, **_kwargs):
        return False


@admin.register(MissionTypeModel)
class MissionTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active"]
    readonly_fields = ["id"]
    list_filter = [
        "is_active",
    ]
    search_fields = ["name"]
    fieldsets = (
        (
            _("Mission Type"),
            {"fields": ("id", "name", "is_active")},
        ),
    )


@admin.register(MissionModel)
class MissionAdmin(AttachmentPreviewMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "service",
        "event",
        "is_active",
        "thumbnail_preview",
        "attachment_preview",
    ]
    readonly_fields = [
        "id",
        "date_joined",
        "date_modified",
        "attachment_preview",
        "thumbnail_preview",
    ]
    list_filter = [
        "service__name",
    ]
    search_fields = ["title", "service__name"]
    inlines = [MissionInteractionInline]
    filter_horizontal = ["type"]

    fieldsets = (
        (
            _("Mission"),
            {
                "fields": (
                    "id",
                    "title",
                    "description",
                    "attachment",
                    "thumbnail",
                    "attachment_preview",
                    "thumbnail_preview",
                )
            },
        ),
        (
            _("Config"),
            {
                "fields": (
                    "order",
                    "type",
                    "service",
                    "service_client",
                    "event",
                    "is_active",
                    "date_joined",
                    "date_modified",
                )
            },
        ),
    )

    @staticmethod
    @admin_method_attributes(short_description=_("Thumbnail preview"))
    def thumbnail_preview(obj):
        if not obj.thumbnail:
            return _("No thumbnail")

        return mark_safe(f'<img src="{obj.thumbnail.url}" width="300px" />')


class LoginQuestionOptionInline(admin.TabularInline):
    model = LoginQuestionOption
    verbose_name_plural = "Options"
    extra = 0
    fields = (
        "id",
        "question",
        "option",
        "order",
    )


class LoginAnswerInline(admin.TabularInline):
    model = LoginAnswer
    verbose_name_plural = "User answers"
    extra = 0
    fields = (
        "option",
        "user",
    )

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LoginQuestions)
class LoginQuestionsAdmin(admin.ModelAdmin):
    list_display = ["id", "question", "event"]
    readonly_fields = ["id"]
    list_filter = [
        "event__service__name",
    ]
    search_fields = ["question", "event__service__name"]
    inlines = [LoginQuestionOptionInline, LoginAnswerInline]

    fieldsets = (
        (_("Question"), {"fields": ("question",)}),
        (_("Config"), {"fields": ("order", "event")}),
    )
