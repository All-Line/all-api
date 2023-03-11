from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.service.models import ServiceModel
from apps.user.models import UserModel
from apps.visual_structure.models import ColorModel, ColorPaletteModel
from utils.abstract_models.base_model import BaseModel

from .utils.file import material_file_directory_path


class CourseCategoryModel(BaseModel):
    title = models.CharField(verbose_name=_("Title"), max_length=255, unique=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    color = models.ForeignKey(
        ColorModel,
        verbose_name=_("Color"),
        related_name="course_categories",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Course Category")
        verbose_name_plural = _("Course Categories")

    def __str__(self):
        return self.title


class CourseModel(BaseModel):
    COURSE_MODE_CHOICES = (("open", _("Open")), ("progressive", _("Progressive")))

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))
    image = models.FileField(
        verbose_name=_("Image"),
        upload_to=material_file_directory_path,
        null=True,
        blank=True,
    )
    trailer = models.FileField(
        verbose_name=_("Trailer"),
        upload_to=material_file_directory_path,
        null=True,
        blank=True,
    )
    is_paid = models.BooleanField(verbose_name=_("Is Paid"), default=True)
    slug = models.SlugField(verbose_name=_("Slug"))
    service = models.ForeignKey(
        ServiceModel,
        verbose_name=_("Service"),
        related_name="courses",
        on_delete=models.CASCADE,
    )
    categories = models.ManyToManyField(
        CourseCategoryModel, related_name="courses", verbose_name=_("Categories")
    )
    color_palette = models.ForeignKey(
        ColorPaletteModel,
        verbose_name=_("Color Palette"),
        related_name="courses",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    course_mode = models.CharField(
        verbose_name=_("Course Mode"),
        default="open",
        choices=COURSE_MODE_CHOICES,
        max_length=255,
        help_text=_(
            "Open so you can access any class at any time. "
            "Progressive so that you can only attend the class "
            "if you have seen the previous one."
        ),
    )

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.title


class LessonModel(BaseModel):
    LESSON_TYPE_CHOICES = (
        ("video", _("Video")),
        ("text", _("Text")),
        ("audio", _("Audio")),
    )

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))
    thumbnail = models.FileField(
        upload_to=material_file_directory_path, verbose_name=_("Thumbnail")
    )
    likes = models.ManyToManyField(
        UserModel, verbose_name=_("Likes"), related_name="lessons_likes"
    )
    course = models.ForeignKey(
        CourseModel,
        verbose_name=_("Course"),
        related_name="lessons",
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(verbose_name=_("Order"), null=True, blank=True)
    lesson_type = models.CharField(
        verbose_name=_("Lesson Type"), choices=LESSON_TYPE_CHOICES, max_length=255
    )
    text = models.TextField(verbose_name=_("Text"), null=True, blank=True)
    reading_time = models.IntegerField(
        help_text=_("In minutes"), verbose_name=_("Reading Time"), null=True, blank=True
    )
    video = models.FileField(
        upload_to=material_file_directory_path,
        verbose_name=_("Video"),
        null=True,
        blank=True,
    )
    video_transcript = models.TextField(
        verbose_name=_("Video Transcription"),
        help_text=_(
            "This is for the accessibility of consumption to the content,"
            " especially to page readers."
        ),
        null=True,
        blank=True,
    )
    audio = models.FileField(
        upload_to=material_file_directory_path,
        verbose_name=_("Audio"),
        null=True,
        blank=True,
    )
    audio_transcript = models.TextField(
        verbose_name=_("Audio Transcription"),
        help_text=_(
            "This is for the accessibility of consumption to the content,"
            " especially to page readers."
        ),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")

    def __str__(self):
        return self.title

    @property
    def likes_amount(self):
        return self.likes.only("id").count()


class CommentModel(BaseModel):
    text = models.TextField(verbose_name=_("Text"))
    lesson = models.ForeignKey(
        LessonModel,
        verbose_name=_("Lesson"),
        related_name="comments",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        UserModel,
        verbose_name=_("Author"),
        related_name="comments",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return f"{self.author.username}'s comment in {self.lesson.title} lesson"
