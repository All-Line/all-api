from unittest.mock import Mock, patch

from django.db import models

from apps.material.models import (
    CommentModel,
    CourseCategoryModel,
    CourseModel,
    LessonModel,
)
from apps.material.models.utils.file import material_file_directory_path
from apps.service.models import ServiceModel
from apps.user.models import UserModel
from apps.visual_structure.models import ColorModel, ColorPaletteModel
from utils.abstract_models.base_model import BaseModel


class TestCourseCategoryModel:
    @classmethod
    def setup_class(cls):
        cls.model = CourseCategoryModel

    def test_str(self):
        course_category = CourseCategoryModel(title="foo bar")

        assert str(course_category) == "foo bar"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Course Category"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Course Categories"

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255
        assert field.unique is True

    def test_description_field(self):
        field = self.model._meta.get_field("description")

        assert type(field) == models.TextField
        assert field.verbose_name == "Description"
        assert field.null is True
        assert field.blank is True

    def test_color_field(self):
        field = self.model._meta.get_field("color")

        assert type(field) == models.ForeignKey
        assert field.related_model == ColorModel
        assert field.verbose_name == "Color"
        assert field.remote_field.related_name == "course_categories"
        assert field.null is True
        assert field.blank is True
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 7


class TestCourseModel:
    @classmethod
    def setup_class(cls):
        cls.model = CourseModel

    def test_str(self):
        color_category = CourseModel(title="foo bar")

        assert str(color_category) == "foo bar"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Course"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Courses"

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255

    def test_description_field(self):
        field = self.model._meta.get_field("description")

        assert type(field) == models.TextField
        assert field.verbose_name == "Description"

    def test_image_field(self):
        field = self.model._meta.get_field("image")

        assert type(field) == models.FileField
        assert field.verbose_name == "Image"
        assert field.upload_to == material_file_directory_path
        assert field.null is True
        assert field.blank is True

    def test_trailer_field(self):
        field = self.model._meta.get_field("trailer")

        assert type(field) == models.FileField
        assert field.verbose_name == "Trailer"
        assert field.upload_to == material_file_directory_path
        assert field.null is True
        assert field.blank is True

    def test_is_paid_field(self):
        field = self.model._meta.get_field("is_paid")

        assert type(field) == models.BooleanField
        assert field.verbose_name == "Is Paid"
        assert field.default is True

    def test_slug_field(self):
        field = self.model._meta.get_field("slug")

        assert type(field) == models.SlugField
        assert field.verbose_name == "Slug"

    def test_service_field(self):
        field = self.model._meta.get_field("service")

        assert type(field) == models.ForeignKey
        assert field.related_model == ServiceModel
        assert field.verbose_name == "Service"
        assert field.remote_field.related_name == "courses"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_categories_field(self):
        field = self.model._meta.get_field("categories")

        assert type(field) == models.ManyToManyField
        assert field.related_model == CourseCategoryModel
        assert field.remote_field.related_name == "courses"
        assert field.verbose_name == "Categories"

    def test_color_palette_field(self):
        field = self.model._meta.get_field("color_palette")

        assert type(field) == models.ForeignKey
        assert field.related_model == ColorPaletteModel
        assert field.verbose_name == "Color Palette"
        assert field.remote_field.related_name == "courses"
        assert field.null is True
        assert field.blank is True
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_course_mode_field(self):
        field = self.model._meta.get_field("course_mode")

        assert type(field) == models.CharField
        assert field.verbose_name == "Course Mode"
        assert field.default == "open"
        assert field.choices == CourseModel.COURSE_MODE_CHOICES
        assert field.max_length == 255
        assert field.help_text == (
            "Open so you can access any class at any time. "
            "Progressive so that you can only attend the class "
            "if you have seen the previous one."
        )

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 13


class TestLessonModel:
    @classmethod
    def setup_class(cls):
        cls.model = LessonModel

    def test_str(self):
        lesson = LessonModel(title="foo bar")

        assert str(lesson) == "foo bar"

    def test_parent_class(self):
        assert issubclass(self.model, BaseModel)

    def test_meta_verbose_name(self):
        assert self.model._meta.verbose_name == "Lesson"

    def test_meta_verbose_name_plural(self):
        assert self.model._meta.verbose_name_plural == "Lessons"

    def test_title_field(self):
        field = self.model._meta.get_field("title")

        assert type(field) == models.CharField
        assert field.verbose_name == "Title"
        assert field.max_length == 255

    def test_description_field(self):
        field = self.model._meta.get_field("description")

        assert type(field) == models.TextField
        assert field.verbose_name == "Description"

    def test_thumbnail_field(self):
        field = self.model._meta.get_field("thumbnail")

        assert type(field) == models.FileField
        assert field.upload_to == material_file_directory_path
        assert field.verbose_name == "Thumbnail"

    def test_likes_field(self):
        field = self.model._meta.get_field("likes")

        assert type(field) == models.ManyToManyField
        assert field.related_model == UserModel
        assert field.verbose_name == "Likes"
        assert field.remote_field.related_name == "lessons_likes"

    def test_course_field(self):
        field = self.model._meta.get_field("course")

        assert type(field) == models.ForeignKey
        assert field.related_model == CourseModel
        assert field.verbose_name == "Course"
        assert field.remote_field.related_name == "lessons"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_order_field(self):
        field = self.model._meta.get_field("order")

        assert type(field) == models.IntegerField
        assert field.verbose_name == "Order"
        assert field.null is True
        assert field.blank is True

    def test_lesson_type_field(self):
        field = self.model._meta.get_field("lesson_type")

        assert type(field) == models.CharField
        assert field.verbose_name == "Lesson Type"
        assert field.choices == LessonModel.LESSON_TYPE_CHOICES
        assert field.max_length == 255

    def test_text_field(self):
        field = self.model._meta.get_field("text")

        assert type(field) == models.TextField
        assert field.verbose_name == "Text"
        assert field.null is True
        assert field.blank is True

    def test_reading_time_field(self):
        field = self.model._meta.get_field("reading_time")

        assert type(field) == models.IntegerField
        assert field.help_text == "In minutes"
        assert field.verbose_name == "Reading Time"
        assert field.null is True
        assert field.blank is True

    def test_video_field(self):
        field = self.model._meta.get_field("video")

        assert type(field) == models.FileField
        assert field.upload_to == material_file_directory_path
        assert field.verbose_name == "Video"
        assert field.null is True
        assert field.blank is True

    def test_video_transcript_field(self):
        field = self.model._meta.get_field("video_transcript")

        assert type(field) == models.TextField
        assert field.verbose_name == "Video Transcription"
        assert field.help_text == (
            "This is for the accessibility of consumption to the content,"
            " especially to page readers."
        )
        assert field.null is True
        assert field.blank is True

    def test_audio_field(self):
        field = self.model._meta.get_field("audio")

        assert type(field) == models.FileField
        assert field.upload_to == material_file_directory_path
        assert field.verbose_name == "Audio"
        assert field.null is True
        assert field.blank is True

    def test_audio_transcript_field(self):
        field = self.model._meta.get_field("audio_transcript")

        assert type(field) == models.TextField
        assert field.verbose_name == "Audio Transcription"
        assert field.help_text == (
            "This is for the accessibility of consumption to the content,"
            " especially to page readers."
        )
        assert field.null is True
        assert field.blank is True

    @patch("apps.material.models.LessonModel.likes")
    def test_likes_amount(self, mock_likes):
        lesson = LessonModel(id=1)
        result = lesson.likes_amount

        mock_likes.only.assert_called_once_with("id")
        mock_likes.only.return_value.count.assert_called_once()

        assert result == mock_likes.only.return_value.count.return_value

    def test_length_fields(self):
        assert len(self.model._meta.fields) == 16


class TestCommentModel:
    @classmethod
    def setup_class(cls):
        cls.model = CommentModel

    def test_str(self):
        comment = CommentModel(
            author=UserModel(username="foo"), lesson=LessonModel(title="bar")
        )
        assert str(comment) == "foo's comment in bar lesson"

    def test_text_field(self):
        field = self.model._meta.get_field("text")

        assert type(field) == models.TextField
        assert field.verbose_name == "Text"

    def test_lesson_field(self):
        field = self.model._meta.get_field("lesson")

        assert type(field) == models.ForeignKey
        assert field.verbose_name == "Lesson"
        assert field.remote_field.related_name == "comments"

    def test_author_field(self):
        field = self.model._meta.get_field("author")

        assert type(field) == models.ForeignKey
        assert field.verbose_name == "Author"
        assert field.remote_field.related_name == "comments"


@patch("apps.material.models.utils.file.datetime")
def test_material_file_directory_path(mock_datetime):
    instance = Mock()
    filename = Mock()
    result = material_file_directory_path(instance, filename)

    mock_datetime.now.assert_called_once()
    mock_datetime.now.return_value.strftime.assert_called_once_with("%d%m%Y_%H:%M:%S")

    assert result == (
        f"media/{instance.title}_"
        f"{mock_datetime.now.return_value.strftime.return_value}_"
        f"{filename}"
    )
