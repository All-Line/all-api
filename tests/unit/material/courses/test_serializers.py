from rest_framework import serializers

from apps.material.models import (
    CommentModel,
    CourseCategoryModel,
    CourseModel,
    LessonModel,
)
from apps.material.serializers import (
    AuthorSerializer,
    CommentSerializer,
    CourseCategorySerializer,
    CourseSerializer,
    LessonSerializer,
)
from apps.user.models import UserModel


class TestAuthorSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = AuthorSerializer

    def test_subclass_serializer(self):
        assert issubclass(AuthorSerializer, serializers.ModelSerializer)

    def test_model(self):
        assert self.serializer.Meta.model == UserModel

    def test_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "username",
            "first_name",
            "last_name",
            "country",
        ]


class TestCommentSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = CommentSerializer

    def test_subclass_serializer(self):
        assert issubclass(CommentSerializer, serializers.ModelSerializer)

    def test_model(self):
        assert self.serializer.Meta.model == CommentModel

    def test_fields(self):
        assert self.serializer.Meta.fields == [
            "date_joined",
            "date_modified",
            "text",
            "author",
        ]


class TestLessonSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = LessonSerializer

    def test_subclass_serializer(self):
        assert issubclass(LessonSerializer, serializers.ModelSerializer)

    def test_model(self):
        assert self.serializer.Meta.model == LessonModel

    def test_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "is_active",
            "title",
            "description",
            "thumbnail",
            "likes",
            "order",
            "lesson_type",
            "text",
            "reading_time",
            "video",
            "video_transcript",
            "audio",
            "audio_transcript",
            "comments",
        ]


class TestCourseCategorySerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = CourseCategorySerializer

    def test_subclass_serializer(self):
        assert issubclass(CourseCategorySerializer, serializers.ModelSerializer)

    def test_model(self):
        assert self.serializer.Meta.model == CourseCategoryModel

    def test_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "is_active",
            "title",
            "description",
            "color",
        ]


class TestCourseSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = CourseSerializer

    def test_subclass_serializer(self):
        assert issubclass(CourseSerializer, serializers.ModelSerializer)

    def test_model(self):
        assert self.serializer.Meta.model == CourseModel

    def test_fields(self):
        assert self.serializer.Meta.fields == [
            "id",
            "is_active",
            "title",
            "description",
            "image",
            "trailer",
            "is_paid",
            "slug",
            "categories",
            "color_palette",
            "course_mode",
            "lessons",
        ]

    def test_depth(self):
        assert self.serializer.Meta.depth == 2
