from django.db import models
from django.utils import timezone

from utils.abstract_models.base_model import BaseModel


class TestBaseModel:
    @classmethod
    def setup_class(cls):
        cls.model = BaseModel

    def test_meta_abstract(self):
        assert self.model._meta.abstract is True

    def test_is_active(self):
        field = self.model._meta.get_field("is_active")

        assert type(field) is models.BooleanField
        assert field.default is True

    def test_date_joined(self):
        field = self.model._meta.get_field("date_joined")

        assert type(field) is models.DateTimeField
        assert field.verbose_name == "date joined"
        assert field.default == timezone.now

    def test_date_modified(self):
        field = self.model._meta.get_field("date_modified")

        assert type(field) is models.DateTimeField
        assert field.verbose_name == "date modified"
        assert field.default == timezone.now
