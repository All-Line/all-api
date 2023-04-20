from unittest.mock import Mock, patch

from django.contrib import admin
from django.contrib.admin import AdminSite

from apps.buying.models import ContractModel
from apps.user.admin import ContractInline, UserAdmin, UserForRetentionAdmin
from apps.user.models import UserModel
from utils.admin.mixins import NoPhysicalDeletionActionMixin


class TestContractInline:
    @classmethod
    def setup_class(cls):
        cls.inline = ContractInline(ContractModel, AdminSite())

    def test_model(self):
        assert self.inline.model == ContractModel

    def test_verbose_name_plural(self):
        assert self.inline.verbose_name_plural == "Contracts"

    def test_fields(self):
        assert self.inline.fields == ("receipt_masked",)

    def test_readonly_fields(self):
        assert self.inline.readonly_fields == self.inline.fields

    def test_extra(self):
        assert self.inline.extra == 0

    @patch("apps.user.admin.mark_safe")
    @patch("apps.user.admin.len")
    def test_receipt_masked_with_receipt_length_less_than_ten(
        self, mock_len, mock_mark_safe
    ):
        receipt = "foo bar"
        mock_contract = Mock(receipt=receipt)
        mock_len.return_value = 7
        receipt_length = mock_len.return_value
        mask = 5 * "*"
        result = self.inline.receipt_masked(mock_contract)

        mock_len.assert_called_once()
        mock_mark_safe.assert_called_once_with(
            f"{receipt[:receipt_length // 2]}"
            f"{mask}"
            f"{receipt[-5:receipt_length]}"
        )
        assert result == mock_mark_safe.return_value

    @patch("apps.user.admin.mark_safe")
    @patch("apps.user.admin.len")
    def test_receipt_masked(self, mock_len, mock_mark_safe):
        receipt = "foo bar test"
        mock_contract = Mock(receipt=receipt)
        mock_len.return_value = 12
        receipt_length = mock_len.return_value
        mask = 5 * "*"
        result = self.inline.receipt_masked(mock_contract)

        mock_len.assert_called_once()
        mock_mark_safe.assert_called_once_with(
            f"{receipt[:5] + mask + receipt[-5:receipt_length]}"
        )
        assert result == mock_mark_safe.return_value

    def test_has_add_permission(self):
        result = self.inline.has_add_permission(None, None)

        assert result is False


class TestUserAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = UserAdmin(UserModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == UserModel

    def test_admin_subclass(self):
        assert issubclass(UserAdmin, NoPhysicalDeletionActionMixin)
        assert issubclass(UserAdmin, admin.ModelAdmin)

    def test_list_display(self):
        assert self.admin.list_display == [
            "id",
            "__str__",
            "service",
            "country",
            "is_verified",
            "is_premium",
        ]

    def test_list_filter(self):
        assert self.admin.list_filter == [
            "service__name",
            "is_premium",
            "birth_date",
            "last_login",
            "date_joined",
        ]

    def test_search_fields(self):
        assert self.admin.search_fields == [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

    def test_actions(self):
        assert self.admin.actions == ["make_premium", "make_superuser"]

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == ["id"]

    def test_inlines(self):
        assert self.admin.inlines == [ContractInline]

    def test_fieldsets_identification(self):
        assert self.admin.fieldsets[0] == (
            "Identification",
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
        )

    def test_fieldsets_profile(self):
        assert self.admin.fieldsets[1] == (
            "Profile",
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
        )

    def test_fieldsets_interaction(self):
        assert self.admin.fieldsets[2] == (
            "Interaction",
            {"fields": ("is_active", "date_joined", "last_login", "event")},
        )

    @patch("apps.user.admin.make_password")
    def test_save_model_with_change_equal_true(self, mock_make_password):
        mock_obj = Mock()
        mock_obj.password = "password"
        mock_form = Mock()
        mock_form.initial.get.return_value = "password"
        self.admin.save_model(None, obj=mock_obj, form=mock_form, change=True)

        mock_form.initial.get.assert_called_once_with("password")
        mock_make_password.assert_not_called()
        mock_obj.save.assert_called_once()

    @patch("apps.user.admin.make_password")
    def test_save_model_with_change_equal_false(self, mock_make_password):
        mock_obj = Mock(password="password")
        mock_form = Mock()
        self.admin.save_model(None, form=mock_form, obj=mock_obj, change=False)

        mock_form.initial.get.assert_called_once_with("password")
        mock_make_password.assert_called_once_with("password")
        mock_obj.save.assert_called_once()
        assert mock_obj.password == mock_make_password.return_value

    def test_make_premium(self):
        mock_queryset = Mock()
        self.admin.make_premium(None, queryset=mock_queryset)

        mock_queryset.update.assert_called_once_with(is_premium=True)

    def test_make_superuser(self):
        mock_queryset = Mock()
        self.admin.make_superuser(None, queryset=mock_queryset)

        mock_queryset.update.assert_called_once_with(
            is_staff=True, is_superuser=True
        )


class TestUserForRetentionAdmin:
    @classmethod
    def setup_class(cls):
        cls.admin = UserForRetentionAdmin(UserModel, AdminSite())

    def test_meta_model(self):
        assert self.admin.model == UserModel

    def test_parent_class(self):
        assert issubclass(UserForRetentionAdmin, UserAdmin)

    def test_fieldsets_fields_to_retention(self):
        assert self.admin.fieldsets[3] == (
            (
                "Fields to Retention",
                {"fields": ("delete_reason",)},
            )
        )

    def test_readonly_fields(self):
        assert self.admin.readonly_fields == [
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

    def test_action(self):
        assert self.admin.actions == ["make_retention", "delete_users"]

    def test_make_retention(self):
        mock_queryset = Mock()
        self.admin.make_retention(None, mock_queryset)

        mock_queryset.update.assert_called_once_with(
            is_active=True, delete_reason=None
        )

    def test_delete_users(self):
        mock_queryset = Mock()
        self.admin.delete_users(None, mock_queryset)

        mock_queryset.update.assert_called_once_with(is_active=False)
