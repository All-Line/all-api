from rest_framework import serializers


class GetAttachmentTypeMixin:
    VIDEO_EXTENSIONS = [
        "mp4",
        "webm",
        "ogg",
        "ogv",
        "avi",
        "mov",
        "wmv",
        "flv",
        "mkv",
    ]

    IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"]

    AUDIO_EXTENSIONS = [
        "mp3",
        "wav",
        "ogg",
        "oga",
        "flac",
        "aac",
        "m4a",
        "wma",
        "alac",
        "aiff",
        "pcm",
        "dsd",
    ]

    @property
    def attachment_type(self):
        attachment = self.attachment

        if attachment.name == "":
            return

        extension = attachment.name.split(".")[-1].lower()

        if extension in self.VIDEO_EXTENSIONS:
            return "video"

        if extension in self.IMAGE_EXTENSIONS:
            return "image"

        if extension in self.AUDIO_EXTENSIONS:
            return "audio"

        return "file"


class GetAttachmentTypeSerializerMixin:
    attachment_type = serializers.SerializerMethodField()

    @staticmethod
    def get_attachment_type(obj):
        return obj.attachment_type
