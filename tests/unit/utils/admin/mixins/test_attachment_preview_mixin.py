from unittest.mock import Mock, patch

from utils.admin.mixins import AttachmentPreviewMixin


class TestAttachmentPreviewMixin:
    @patch("utils.admin.mixins.mark_safe")
    def test_attachment_preview_without_attachment(self, mock_mark_safe):
        mock_obj = Mock(attachment=None)

        assert AttachmentPreviewMixin.attachment_preview(mock_obj) == "No attachment"

        mock_mark_safe.assert_not_called()

    @patch("utils.admin.mixins.mark_safe")
    def test_attachment_preview_without_available_preview(self, mock_mark_safe):
        mock_obj = Mock(attachment_type="invalid")

        assert (
            AttachmentPreviewMixin.attachment_preview(mock_obj)
            == "No preview available"
        )

        mock_mark_safe.assert_not_called()

    @patch("utils.admin.mixins.mark_safe")
    def test_attachment_preview_with_available_preview(self, mock_mark_safe):
        mock_obj = Mock(attachment_type="image")

        AttachmentPreviewMixin.attachment_preview(mock_obj)

        mock_mark_safe.assert_called_once_with(
            f'<img src="{mock_obj.attachment.url}" width="300px" />'
        )
