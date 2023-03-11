from unittest.mock import Mock, patch

from django.contrib import admin
from django.contrib.admin import AdminSite

from apps.buying.admin import ContractAdmin, PackageAdmin, PackageInline, StoreAdmin
from apps.buying.models import ContractModel, PackageModel, StoreModel


class TestPackageInline:
    @classmethod
    def setup_class(cls):
        cls.inline = PackageInline(PackageModel, AdminSite())

    def test_meta_model(self):
        assert self.inline.model == PackageModel

    def test_admin_subclass(self):
        assert issubclass(PackageInline, admin.TabularInline)

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Packages"

    def test_extra_field(self):
        assert self.inline.extra == 0

    def test_inline_fields(self):
        assert self.inline.fields == (
            "label",
            "price",
            "slug",
            "service",
        )


class TestStoreAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = StoreAdmin(StoreModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == StoreModel

    def test_admin_subclass(self):
        assert issubclass(StoreAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "name",
            "backend",
            "total_packages",
            "date_joined",
        ]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == [
            "id",
        ]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
            {"fields": ("name", "backend")},
        )

    @patch("apps.buying.admin.mark_safe")
    def test_total_packages(self, mock_mark_safe):
        mock_store = Mock()
        result = self.admin.total_packages(mock_store)

        mock_store.packages.filter.assert_called_once_with(is_active=True)
        mock_store.packages.filter.return_value.count.assert_called_once()
        mock_mark_safe.assert_called_once_with(
            f"<p>{mock_store.packages.filter.return_value.count.return_value}</p>"
        )
        assert result == mock_mark_safe.return_value


class TestPackageAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = PackageAdmin(PackageModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == PackageModel

    def test_admin_subclass(self):
        assert issubclass(PackageAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "slug",
            "service",
            "price",
            "store",
            "sales_amount",
        ]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id"]

    def test_search_fields(self):
        assert self.admin.search_fields == ["slug", "id"]

    def test_list_filter(self):
        assert self.admin.list_filter == ["service__name", "price"]

    def test_filter_horizontal(self):
        assert self.admin.filter_horizontal == ["courses"]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
            {"fields": ("label", "price", "slug")},
        )

    def test_fieldsets_settings(self):
        assert self.admin.fieldsets[1] == (
            "Settings",
            {"fields": ("store", "courses", "service")},
        )

    @patch("apps.buying.admin.mark_safe")
    def test_sales_amount(self, mock_mark_safe):
        mock_package = Mock()
        result = self.admin.sales_amount(mock_package)

        mock_package.contracts.filter.assert_called_once_with(is_active=True)
        mock_package.contracts.filter.return_value.count.assert_called_once()
        mock_mark_safe.assert_called_once_with(
            f"<p>{mock_package.contracts.filter.return_value.count.return_value}</p>"
        )
        assert result == mock_mark_safe.return_value


class TestContractAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = ContractAdmin(ContractModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == ContractModel

    def test_admin_subclass(self):
        assert issubclass(ContractAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == ["id", "user", "package", "is_active"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id", "package", "user", "receipt"]

    def test_search_fields(self):
        assert self.admin.search_fields == ["id"]

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "package__slug",
            "is_active",
            "package__service__name",
        ]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
            {"fields": ("receipt",)},
        )

    def test_fieldsets_settings(self):
        assert self.admin.fieldsets[1] == (
            "Settings",
            {"fields": ("package", "user")},
        )
