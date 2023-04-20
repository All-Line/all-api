from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from utils.admin.mixins import NoPhysicalDeletionActionMixin

from ..buying.models import ContractModel
from .models import UserForRetentionProxy, UserModel


class ContractInline(admin.TabularInline):
    model = ContractModel
    verbose_name_plural = _("Contracts")
    fields = ("receipt_masked",)
    readonly_fields = fields
    extra = 0

    @staticmethod
    def receipt_masked(contract):
        receipt = contract.receipt
        receipt_length = len(receipt)
        mask = 5 * "*"

        if receipt_length < 10:
            return mark_safe(
                f"{receipt[:receipt_length // 2] + mask + receipt[-5:receipt_length]}"
            )

        return mark_safe(f"{receipt[:5] + mask + receipt[-5:receipt_length]}")

    def has_add_permission(self, request, obj):
        return False


@admin.register(UserModel)
class UserAdmin(NoPhysicalDeletionActionMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "__str__",
        "service",
        "country",
        "is_verified",
        "is_premium",
    ]
    readonly_fields = ["id"]
    list_filter = [
        "service__name",
        "is_premium",
        "birth_date",
        "last_login",
        "date_joined",
    ]
    search_fields = ["username", "first_name", "last_name", "email"]
    actions = ["make_premium", "make_superuser"]
    inlines = [ContractInline]
    fieldsets = (
        (
            _("Identification"),
            {
                "fields": (
                    "id",
                    "service",
                    "first_name",
                    "last_name",
                    "country",
                    "document",
                    "birth_date",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (
            _("Profile"),
            {
                "fields": (
                    "profile_image",
                    "email",
                    "password",
                    "username",
                    "is_verified",
                    "is_premium",
                )
            },
        ),
        (
            _("Interaction"),
            {"fields": ("is_active", "date_joined", "last_login", "event")},
        ),
    )

    def save_model(self, _, obj, form, change):
        initial_password = form.initial.get("password")
        modified_password = obj.password
        has_password_modified = initial_password != modified_password

        if not change or has_password_modified:
            obj.password = make_password(obj.password)
        obj.save()

    @admin.action(description=_("Mark selected users as premium"))
    def make_premium(self, _, queryset):
        queryset.update(is_premium=True)

    @admin.action(description=_("Mark selected users as SUPERUSER ⚠"))
    def make_superuser(self, _, queryset):
        queryset.update(is_staff=True, is_superuser=True)


@admin.register(UserForRetentionProxy)
class UserForRetentionAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            _("Fields to Retention"),
            {"fields": ("delete_reason",)},
        ),
    )
    readonly_fields = [
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "password",
        "is_staff",
        "is_active",
        "is_superuser",
        "date_joined",
        "is_verified",
        "is_premium",
        "document",
        "birth_date",
        "last_login",
        "country",
        "profile_image",
        "service",
        "delete_reason",
    ]
    actions = ["make_retention", "delete_users"]

    @admin.action(description=_("Selected users have been retained"))
    def make_retention(self, _, queryset):
        queryset.update(is_active=True, delete_reason=None)

    @admin.action(description=_("Delete users"))
    def delete_users(self, _, queryset):
        queryset.update(is_active=False)


admin.site.unregister(Group)
