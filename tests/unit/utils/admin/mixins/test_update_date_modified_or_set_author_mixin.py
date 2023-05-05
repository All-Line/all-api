from unittest.mock import Mock, patch

from utils.admin.mixins import UpdateDateModifiedOrSetAuthorMixin


class TestUpdateDateModifiedOrSetAuthorMixin:
    @patch("utils.admin.mixins.super")
    @patch("utils.admin.mixins.timezone")
    def test_save_model_with_change_equal_true(self, mock_timezone, mock_super):
        mixin = UpdateDateModifiedOrSetAuthorMixin()
        mock_obj = Mock()
        mixin.save_model(None, form=None, obj=mock_obj, change=True)

        mock_obj.save.assert_called_once()
        mock_timezone.now.assert_called_once()
        mock_super.assert_called_once()
        mock_super.return_value.save_model.assert_called_once_with(
            None, mock_obj, None, True
        )
        assert mock_obj.date_modified == mock_timezone.now.return_value

    @patch("utils.admin.mixins.super")
    @patch("utils.admin.mixins.timezone")
    def test_save_model_with_change_equal_false(self, mock_timezone, mock_super):
        mixin = UpdateDateModifiedOrSetAuthorMixin()
        mock_obj = Mock()
        mock_request = Mock()
        mixin.save_model(mock_request, form=None, obj=mock_obj, change=False)

        mock_obj.save.assert_called_once()
        mock_timezone.now.assert_not_called()
        mock_super.assert_called_once()
        mock_super.return_value.save_model.assert_called_once_with(
            mock_request, mock_obj, None, False
        )
        assert mock_obj.author == mock_request.user
