from unittest.mock import Mock, patch

from django.contrib import admin

from apps.service.admin import ServiceEmailConfigInline
from apps.social.admin import (
    EventAdmin,
    LoginAnswerInline,
    MissionAdmin,
    MissionInteractionAdmin,
    MissionInteractionInline,
    PostAdmin,
    PostCommentAdmin,
    PostCommentInline,
    PostInline,
)
from apps.social.models import (
    EventModel,
    LoginAnswer,
    MissionInteractionModel,
    MissionModel,
    PostCommentModel,
    PostModel,
)
from utils.admin.mixins import (
    AttachmentPreviewMixin,
    UpdateDateModifiedMixin,
    UpdateDateModifiedOrSetAuthorMixin,
)


class TestPostCommentInline:
    @classmethod
    def setup_class(cls):
        cls.inline = PostCommentInline(PostCommentModel, admin.AdminSite())

    def test_model(self):
        assert self.inline.model == PostCommentModel

    def test_inline_subclass(self):
        assert issubclass(PostCommentInline, admin.TabularInline)

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Comments"

    def test_fields(self):
        assert self.inline.fields == (
            "id",
            "content",
            "author",
            "reactions_amount",
        )

    def test_readonly_fields(self):
        assert self.inline.readonly_fields == self.inline.fields

    def test_extra(self):
        assert self.inline.extra == 0

    def test_has_add_permission(self):
        result = self.inline.has_add_permission(None, None)

        assert result is False


class TestPostAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = PostAdmin(PostModel, admin.AdminSite())

    def test_meta_model(self):
        assert self.admin.model == PostModel

    def test_admin_subclass(self):
        assert issubclass(PostAdmin, admin.ModelAdmin)
        assert issubclass(PostAdmin, UpdateDateModifiedOrSetAuthorMixin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "author",
            "service",
            "reactions_amount",
            "attachment_preview",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == ["service__name"]

    def test_search_fields(self):
        assert self.admin.search_fields == [
            "description",
            "author__first_name",
            "service__name",
        ]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == [
            "id",
            "author",
            "ai_report",
            "attachment_preview",
        ]

    def test_inlines(self):
        assert self.admin.inlines == [PostCommentInline]

    def test_fieldsets_post(self):
        assert self.admin.fieldsets[0] == (
            "Post",
            {"fields": ("description", "attachment", "attachment_preview")},
        )

    def test_fieldsets_ai_report(self):
        assert self.admin.fieldsets[1] == (
            "AI Report",
            {"fields": ("ai_text_report", "ai_report")},
        )

    def test_fieldsets_config(self):
        assert self.admin.fieldsets[2] == (
            "Config",
            {"fields": ("author", "service", "event")},
        )

    def test_actions(self):
        assert self.admin.actions == ["generate_ai_report"]

    def test_generate_ai_report(self):
        post_1 = Mock()
        post_2 = Mock()
        queryset = [post_1, post_2]
        self.admin.generate_ai_report(None, queryset)

        post_1.generate_ai_text_report.assert_called_once()
        post_2.generate_ai_text_report.assert_called_once()


class TestPostCommentAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = PostCommentAdmin(PostCommentModel, admin.AdminSite())

    def test_meta_model(self):
        assert self.admin.model == PostCommentModel

    def test_admin_subclass(self):
        assert issubclass(PostCommentAdmin, admin.ModelAdmin)
        assert issubclass(PostCommentAdmin, UpdateDateModifiedOrSetAuthorMixin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "author",
            "post",
            "reactions_amount",
            "is_deleted",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "post__service__name",
            "author__first_name",
            "post",
        ]

    def test_search_fields(self):
        assert self.admin.search_fields == [
            "content",
            "author__first_name",
            "post__service__name",
        ]

    def test_fieldsets_post(self):
        assert self.admin.fieldsets[0] == (
            "Comment",
            {"fields": ("content", "is_deleted")},
        )

    def test_fieldsets_config(self):
        assert self.admin.fieldsets[1] == (
            "Config",
            {"fields": ("author", "post")},
        )


class TestPostInline:
    @classmethod
    def setup_class(cls):
        cls.inline = PostInline(PostModel, admin.AdminSite())

    def test_model(self):
        assert self.inline.model == PostModel

    def test_inline_subclass(self):
        assert issubclass(PostInline, admin.TabularInline)

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Posts"

    def test_fields(self):
        assert self.inline.fields == (
            "id",
            "description",
            "attachment",
            "attachment_preview",
            "reactions_amount",
        )

    def test_readonly_fields(self):
        assert self.inline.readonly_fields == self.inline.fields

    def test_extra(self):
        assert self.inline.extra == 0


class TestEventAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = EventAdmin(EventModel, admin.AdminSite())

    def test_meta_model(self):
        assert self.admin.model == EventModel

    def test_admin_subclass(self):
        assert issubclass(EventAdmin, admin.ModelAdmin)
        assert issubclass(EventAdmin, UpdateDateModifiedMixin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "title",
            "service",
            "event_type",
            "is_active",
            "attachment_preview",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "service__name",
        ]

    def test_search_fields(self):
        assert self.admin.search_fields == ["title", "service__name"]

    def test_fieldsets_event(self):
        assert self.admin.fieldsets[0] == (
            "Event",
            {
                "fields": (
                    "title",
                    "description",
                    "event_type",
                    "attachment",
                    "attachment_preview",
                )
            },
        )

    def test_fieldsets_config(self):
        assert self.admin.fieldsets[1] == (
            "Config",
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
        )

    def test_inlines(self):
        assert self.admin.inlines == [ServiceEmailConfigInline, PostInline]

    def test_send_invite_to_guests(self):
        events = [Mock(), Mock()]
        self.admin.send_invite_to_guests(None, events)

        events[0].create_guests.assert_called_once()
        events[1].create_guests.assert_called_once()


class TestMissionInteractionInline:
    @classmethod
    def setup_class(cls):
        cls.inline = MissionInteractionInline(
            MissionInteractionModel, admin.AdminSite()
        )

    def test_model(self):
        assert self.inline.model == MissionInteractionModel

    def test_inline_subclass(self):
        assert issubclass(MissionInteractionInline, admin.TabularInline)

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Interactions"

    def test_fields(self):
        assert self.inline.fields == (
            "id",
            "mission",
            "user",
            "attachment",
            "attachment_preview",
            "content",
            "date_joined",
        )

    def test_readonly_fields(self):
        assert self.inline.readonly_fields == self.inline.fields

    def test_extra(self):
        assert self.inline.extra == 0

    def test_has_add_permission(self):
        result = self.inline.has_add_permission(None, None)

        assert result is False


class TestMissionInteractionAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = MissionInteractionAdmin(MissionInteractionModel, admin.AdminSite())

    def test_meta_model(self):
        assert self.admin.model == MissionInteractionModel

    def test_admin_subclass(self):
        assert issubclass(MissionInteractionAdmin, admin.ModelAdmin)
        assert issubclass(MissionInteractionAdmin, AttachmentPreviewMixin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "mission",
            "user",
            "date_joined",
            "attachment_preview",
            "is_active",
        ]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == [
            "id",
            "mission",
            "user",
            "date_joined",
            "attachment_preview",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "mission__service__name",
            "mission__event__title",
            "mission__is_active",
            "mission",
        ]

    def test_has_add_permission(self):
        result = self.admin.has_add_permission(None, None)

        assert result is False


class TestMissionAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = MissionAdmin(MissionModel, admin.AdminSite())

    def test_meta_model(self):
        assert self.admin.model == MissionModel

    def test_admin_subclass(self):
        assert issubclass(MissionAdmin, admin.ModelAdmin)
        assert issubclass(MissionAdmin, AttachmentPreviewMixin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "title",
            "service",
            "event",
            "is_active",
            "thumbnail_preview",
            "attachment_preview",
        ]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == [
            "id",
            "date_joined",
            "date_modified",
            "attachment_preview",
            "thumbnail_preview",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "service__name",
        ]

    def test_search_fields(self):
        assert self.admin.search_fields == ["title", "service__name"]

    def test_inlines(self):
        assert self.admin.inlines == [MissionInteractionInline]

    def test_filter_horizontal(self):
        assert self.admin.filter_horizontal == ["type"]

    def test_fieldsets_mission(self):
        assert self.admin.fieldsets[0] == (
            "Mission",
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
        )

    def test_fieldsets_config(self):
        assert self.admin.fieldsets[1] == (
            "Config",
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
        )

    @patch("apps.social.admin.mark_safe")
    def test_thumbnail_preview_without_thumbnail(self, mock_mark_safe):
        mock_obj = Mock(thumbnail=None)
        result = self.admin.thumbnail_preview(mock_obj)

        assert result == "No thumbnail"
        mock_mark_safe.assert_not_called()

    @patch("apps.social.admin.mark_safe")
    def test_thumbnail_preview_with_thumbnail(self, mock_mark_safe):
        mock_obj = Mock()
        self.admin.thumbnail_preview(mock_obj)

        mock_mark_safe.assert_called_once_with(
            f'<img src="{mock_obj.thumbnail.url}" width="300px" />'
        )


class TestLoginAnswerInline:
    @classmethod
    def setup_class(cls):
        cls.inline = LoginAnswerInline(LoginAnswer, admin.AdminSite())

    def test_model(self):
        assert self.inline.model == LoginAnswer

    def test_inline_subclass(self):
        assert issubclass(LoginAnswerInline, admin.TabularInline)

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "User answers"

    def test_fields(self):
        assert self.inline.fields == (
            "option",
            "user",
        )

    def test_extra(self):
        assert self.inline.extra == 0

    def test_has_add_permission(self):
        result = self.inline.has_add_permission(None, None)

        assert result is False

    def test_has_change_permission(self):
        result = self.inline.has_change_permission(None, None)

        assert result is False
