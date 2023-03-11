from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.buying.models import ContractModel, PackageModel, StoreModel


class PackageInline(admin.TabularInline):
    model = PackageModel
    verbose_name_plural = _("Packages")
    extra = 0
    fields = (
        "label",
        "price",
        "slug",
        "service",
    )


@admin.register(StoreModel)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "backend", "total_packages", "date_joined"]
    readonly_fields = ["id"]
    fieldsets = ((_("Identification"), {"fields": ("name", "backend")}),)
    inlines = [PackageInline]

    @staticmethod
    def total_packages(store):
        return mark_safe(f"<p>{store.packages.filter(is_active=True).count()}</p>")


@admin.register(PackageModel)
class PackageAdmin(admin.ModelAdmin):
    list_display = ["id", "slug", "service", "price", "store", "sales_amount"]
    readonly_fields = ["id"]
    search_fields = ["slug", "id"]
    list_filter = ["service__name", "price"]
    filter_horizontal = ["courses"]
    fieldsets = (
        (
            _("Identification"),
            {
                "fields": (
                    "label",
                    "price",
                    "slug",
                )
            },
        ),
        (_("Settings"), {"fields": ("store", "courses", "service")}),
    )

    @staticmethod
    def sales_amount(package):
        return mark_safe(f"<p>{package.contracts.filter(is_active=True).count()}</p>")


@admin.register(ContractModel)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "package", "is_active"]
    readonly_fields = ["id", "package", "user", "receipt"]
    search_fields = ["id"]
    list_filter = ["package__slug", "is_active", "package__service__name"]
    fieldsets = (
        (
            _("Identification"),
            {"fields": ("receipt",)},
        ),
        (_("Settings"), {"fields": ("package", "user")}),
    )
