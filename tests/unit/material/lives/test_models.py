from django.db import models

from apps.material.models import LiveModel
from apps.material.models.utils.file import material_file_directory_path
from apps.service.models import ServiceModel
from utils.abstract_models.base_model import BaseModel


class TestLiveModel:
    @classmethod
    def setup_class(cls):
        cls.model = LiveModel

    def test_str(self):
        live = LiveModel(title="foo bar")

        assert str(live) == "foo bar"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Live"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Lives"

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255

    def test_description_field(self):
        field = self.model._meta.get_field("description")

        assert type(field) == models.TextField
        assert field.verbose_name == "Description"

    def test_slug_field(self):
        field = self.model._meta.get_field("slug")

        assert type(field) == models.SlugField
        assert field.verbose_name == "Slug"

    def test_is_paid_field(self):
        field = self.model._meta.get_field("is_paid")

        assert type(field) == models.BooleanField
        assert field.verbose_name == "Is Paid"
        assert field.default is True

    def test_starts_at_field(self):
        field = self.model._meta.get_field("starts_at")

        assert type(field) == models.DateTimeField
        assert field.verbose_name == "Starts At"
        assert field.help_text == "The day and time the live will start"

    def test_integration_field_field(self):
        field = self.model._meta.get_field("integration_field")

        assert type(field) == models.TextField
        assert field.verbose_name == "Integration Field"
        assert field.help_text == (
            "This field controls the integration that will be made for the Live to "
            "happen. Fields like Youtube ID, Vimeo ID, Zoom JSON, etc are accepted."
        )

    def test_live_type_field(self):
        field = self.model._meta.get_field("live_type")

        assert type(field) == models.CharField
        assert field.verbose_name == "Type"
        assert field.max_length == 255
        assert field.choices == LiveModel.LIVE_TYPE_CHOICES

    def test_image_field(self):
        field = self.model._meta.get_field("image")

        assert type(field) == models.FileField
        assert field.verbose_name == "Image"
        assert field.upload_to == material_file_directory_path
        assert field.null is True
        assert field.blank is True

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.verbose_name == "Service"
        assert field.related_model == ServiceModel
        assert field.remote_field.related_name == "lives"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 13
