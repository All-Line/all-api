from rest_framework import serializers

from apps.material.models import (
    CommentModel,
    CourseCategoryModel,
    CourseModel,
    LessonModel,
)
from apps.user.models import UserModel
from apps.visual_structure.serializers import ColorPaletteSerializer, ColorSerializer


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "username", "first_name", "last_name", "country"]


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = CommentModel
        fields = [
            "date_joined",
            "date_modified",
            "text",
            "author",
        ]


class LessonSerializer(serializers.ModelSerializer):
    likes = AuthorSerializer(many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = LessonModel
        fields = [
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


class CourseCategorySerializer(serializers.ModelSerializer):
    color = ColorSerializer()

    class Meta:
        model = CourseCategoryModel
        fields = [
            "id",
            "is_active",
            "title",
            "description",
            "color",
        ]


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)
    categories = CourseCategorySerializer(many=True)
    color_palette = ColorPaletteSerializer()

    class Meta:
        model = CourseModel
        fields = [
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
        depth = 2
