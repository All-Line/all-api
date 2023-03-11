from django.db import models

from apps.buying.backends import DummyBackend
from apps.buying.models import ContractModel, PackageModel, StoreModel
from apps.material.models import CourseModel
from apps.service.models import ServiceModel
from apps.user.models import UserModel
from utils.abstract_models.base_model import BaseModel


class TestStoreModel:
    @classmethod
    def setup_class(cls):
        cls.model = StoreModel

    def test_str(self):
        store = StoreModel(name="foo")

        assert str(store) == "foo"

    def test_parent_class(self):
        assert issubclass(StoreModel, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Store"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Stores"

    def test_name_field(self):
        field = self.model._meta.get_field("name")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255
        assert field.unique is True

    def test_backend_field(self):
        field = self.model._meta.get_field("backend")

        assert type(field) == models.CharField
        assert field.verbose_name == "Integration Backend"
        assert field.max_length == 255
        assert field.choices == StoreModel.BACKEND_CHOICES

    def test_get_backend(self):
        store = StoreModel(backend="dummy")
        result = store.get_backend()

        assert isinstance(result, DummyBackend)

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 6


class TestPackageModel:
    @classmethod
    def setup_class(cls):
        cls.model = PackageModel

    def test_str(self):
        package: PackageModel = PackageModel(label="some label")

        assert str(package) == "some label"

    def test_parent_class(self):
        assert issubclass(PackageModel, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Package"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Packages"

    def test_label_field(self):
        field = self.model._meta.get_field("label")

        assert type(field) == models.CharField
        assert field.verbose_name == "Label"
        assert field.max_length == 255

    def test_price_field(self):
        field = self.model._meta.get_field("price")

        assert type(field) == models.FloatField
        assert field.verbose_name == "Price"

    def test_slug_field(self):
        field = self.model._meta.get_field("slug")

        assert type(field) == models.SlugField
        assert field.verbose_name == "Slug"

    def test_store_field(self):
        field = self.model._meta.get_field("store")

        assert type(field) == models.ForeignKey
        assert field.related_model is StoreModel
        assert field.remote_field.related_name == "packages"
        assert field.verbose_name == "Store"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_courses_field(self):
        field = self.model._meta.get_field("courses")

        assert type(field) == models.ManyToManyField
        assert field.related_model is CourseModel
        assert field.remote_field.related_name == "packages"
        assert field.verbose_name == "Courses"

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model is ServiceModel
        assert field.remote_field.related_name == "packages"
        assert field.verbose_name == "Service"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 9


class TestContractModel:
    @classmethod
    def setup_class(cls):
        cls.model = ContractModel

    def test_str(self):
        user = UserModel(first_name="foo", last_name="bar")
        contract = ContractModel(user=user)

        assert str(contract) == "Contract for foo bar"

    def test_parent_class(self):
        assert issubclass(ContractModel, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Contract"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Contracts"

    def test_receipt_field(self):
        field = self.model._meta.get_field("receipt")

        assert type(field) == models.TextField
        assert field.verbose_name == "Receipt"

    def test_package_field(self):
        field = self.model._meta.get_field("package")

        assert type(field) == models.ForeignKey
        assert field.related_model is PackageModel
        assert field.verbose_name == "Package"
        assert field.remote_field.related_name == "contracts"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_user_field(self):
        field = self.model._meta.get_field("user")

        assert type(field) == models.ForeignKey
        assert field.related_model is UserModel
        assert field.verbose_name == "User"
        assert field.remote_field.related_name == "contracts"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 7
