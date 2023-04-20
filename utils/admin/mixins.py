from django.utils import timezone


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
