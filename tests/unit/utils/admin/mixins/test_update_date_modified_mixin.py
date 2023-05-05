from unittest.mock import Mock, patch

from utils.admin.mixins import UpdateDateModifiedMixin


class TestUpdateDateModifiedMixin:
    @patch("utils.admin.mixins.timezone")
    @patch("utils.admin.mixins.super")
    def test_save_model_with_change_equal_true(self, mock_super, mock_timezone):
        mixin = UpdateDateModifiedMixin()
        mock_obj = Mock()
        mixin.save_model(None, form=None, obj=mock_obj, change=True)

        mock_obj.save.assert_called_once()
        mock_timezone.now.assert_called_once()
        mock_super.assert_called_once()
        mock_super.return_value.save_model.assert_called_once_with(
            None, mock_obj, None, True
        )
        assert mock_obj.date_modified == mock_timezone.now.return_value
