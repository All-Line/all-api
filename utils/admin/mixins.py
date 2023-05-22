from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from utils.admin import admin_method_attributes


class NoPhysicalDeletionActionMixin:
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions


class UpdateDateModifiedMixin:
    def save_model(self, request, obj, form, change):
        if change:
            obj.date_modified = timezone.now()
            obj.save()
        super().save_model(request, obj, form, change)


class UpdateDateModifiedOrSetAuthorMixin:
    def save_model(self, request, obj, form, change):
        if change:
            obj.date_modified = timezone.now()
        else:
            obj.author = request.user
        obj.save()
        super().save_model(request, obj, form, change)


class AttachmentPreviewMixin:
    @staticmethod
    @admin_method_attributes(short_description=_("Attachment preview"))
    def attachment_preview(obj):
        if not obj.attachment:
            return _("No attachment")

        attachment_type = obj.attachment_type
        attachment_map = {
            "image": f'<img src="{obj.attachment.url}" width="300px" />',
            "video": f'<video src="{obj.attachment.url}" width="300px" controls />',
            "audio": f'<audio src="{obj.attachment.url}" width="300px" controls />',
        }

        return (
            mark_safe(attachment_map[attachment_type])
            if attachment_type in attachment_map
            else "No preview available"
        )
