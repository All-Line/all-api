from django.contrib import admin

from apps.social.admin import (
    EventAdmin,
    PostAdmin,
    PostCommentAdmin,
    PostCommentInline,
    PostInline,
)
from apps.social.models import EventModel, PostCommentModel, PostModel
from utils.admin.mixins import (
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
        assert self.admin.readonly_fields == ["id", "author"]

    def test_inlines(self):
        assert self.admin.inlines == [PostCommentInline]

    def test_fieldsets_post(self):
        assert self.admin.fieldsets[0] == (
            "Post",
            {"fields": ("description", "attachment")},
        )

    def test_fieldsets_config(self):
        assert self.admin.fieldsets[1] == (
            "Config",
            {"fields": ("author", "service", "event")},
        )


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
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "post__service__name",
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
            {"fields": ("content",)},
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
            {"fields": ("title", "description", "event_type", "attachment")},
        )

    def test_fieldsets_config(self):
        assert self.admin.fieldsets[1] == (
            "Config",
            {
                "fields": (
                    "guests",
                    "send_email_to_guests",
                    "event_link",
                    "service",
                    "is_active",
                    "date_joined",
                    "date_modified",
                )
            },
        )

    def test_inlines(self):
        assert self.admin.inlines == [PostInline]
