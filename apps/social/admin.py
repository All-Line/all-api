from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.social.models import (
    EventModel,
    LoginAnswer,
    LoginQuestionOption,
    LoginQuestions,
    MissionInteractionModel,
    MissionModel,
    PostCommentModel,
    PostModel,
    ReactionTypeModel,
)
from utils.admin.mixins import (
    UpdateDateModifiedMixin,
    UpdateDateModifiedOrSetAuthorMixin,
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
class PostAdmin(UpdateDateModifiedOrSetAuthorMixin, admin.ModelAdmin):
    list_display = ["id", "author", "service", "reactions_amount", "type"]
    readonly_fields = ["id", "author"]
    list_filter = [
        "service__name",
    ]
    search_fields = ["description", "author__first_name", "service__name"]
    inlines = [PostCommentInline]

    fieldsets = (
        (_("Post"), {"fields": ("description", "attachment")}),
        (_("Config"), {"fields": ("author", "service", "event", "type")}),
    )


@admin.register(PostCommentModel)
class PostCommentAdmin(UpdateDateModifiedOrSetAuthorMixin, admin.ModelAdmin):
    list_display = ["id", "author", "post", "reactions_amount"]
    readonly_fields = ["id", "author"]
    list_filter = [
        "post__service__name",
    ]
    search_fields = ["content", "author__first_name", "post__service__name"]

    fieldsets = (
        (_("Comment"), {"fields": ("content",)}),
        (_("Config"), {"fields": ("author", "post")}),
    )


class PostInline(admin.TabularInline):
    model = PostModel
    verbose_name_plural = "Posts"
    extra = 0
    fields = ("id", "type", "description", "attachment", "reactions_amount")
    readonly_fields = fields


@admin.register(EventModel)
class EventAdmin(UpdateDateModifiedMixin, admin.ModelAdmin):
    list_display = ["id", "title", "service", "event_type", "is_active"]
    readonly_fields = ["id", "date_joined", "date_modified"]
    list_filter = [
        "service__name",
    ]
    search_fields = ["title", "service__name"]
    inlines = [PostInline]

    fieldsets = (
        (
            _("Event"),
            {"fields": ("title", "description", "event_type", "attachment")},
        ),
        (
            _("Config"),
            {
                "fields": (
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


@admin.register(ReactionTypeModel)
class ReactionTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "service"]
    list_filter = [
        "service__name",
    ]

    fieldsets = ((_("Config"), {"fields": ("name", "attachment", "service")}),)


class MissionInteractionInline(admin.TabularInline):
    model = MissionInteractionModel
    verbose_name_plural = "Interactions"
    extra = 0
    fields = (
        "id",
        "mission",
        "user",
        "attachment",
        "content",
        "date_joined",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj):
        return False


@admin.register(MissionModel)
class MissionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "service", "event", "is_active"]
    readonly_fields = ["id", "date_joined", "date_modified"]
    list_filter = [
        "service__name",
    ]
    search_fields = ["title", "service__name"]
    inlines = [MissionInteractionInline]

    fieldsets = (
        (_("Mission"), {"fields": ("id", "title", "description", "attachment")}),
        (
            _("Config"),
            {
                "fields": (
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
    verbose_name_plural = "Answers"
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
