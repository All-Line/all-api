from unittest.mock import Mock

from utils.mixins.attachment_type import (
    GetAttachmentTypeMixin,
    GetAttachmentTypeSerializerMixin,
)


class TestGetAttachmentTypeMixin:
    def test_video_extensions(self):
        assert GetAttachmentTypeMixin.VIDEO_EXTENSIONS == [
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

    def test_image_extensions(self):
        assert GetAttachmentTypeMixin.IMAGE_EXTENSIONS == [
            "jpg",
            "jpeg",
            "png",
            "gif",
            "bmp",
            "svg",
            "webp",
        ]

    def test_audio_extensions(self):
        assert GetAttachmentTypeMixin.AUDIO_EXTENSIONS == [
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

    def test_attachment_type(self):
        class Attachment:
            def __init__(self, name):
                self.name = name

        class AttachmentType(GetAttachmentTypeMixin):
            def __init__(self, attachment):
                self.attachment = attachment

        attachment = Attachment("video.mp4")
        attachment_type = AttachmentType(attachment)

        assert attachment_type.attachment_type == "video"

        attachment = Attachment("image.jpg")
        attachment_type = AttachmentType(attachment)

        assert attachment_type.attachment_type == "image"

        attachment = Attachment("audio.mp3")
        attachment_type = AttachmentType(attachment)

        assert attachment_type.attachment_type == "audio"

        attachment = Attachment("file.txt")
        attachment_type = AttachmentType(attachment)

        assert attachment_type.attachment_type == "file"

        attachment = Attachment("")
        attachment_type = AttachmentType(attachment)

        assert attachment_type.attachment_type is None


class TestGetAttachmentTypeSerializerMixin:
    def test_get_attachment_type(self):
        mock_obj = Mock()
        assert (
            GetAttachmentTypeSerializerMixin.get_attachment_type(mock_obj)
            == mock_obj.attachment_type
        )
