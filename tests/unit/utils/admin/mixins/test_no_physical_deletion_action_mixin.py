from unittest.mock import Mock, patch

from utils.admin.mixins import NoPhysicalDeletionActionMixin


class TestNoPhysicalDeletionActionMixin:
    @classmethod
    def setup_class(cls):
        cls.mixin = NoPhysicalDeletionActionMixin

    @patch("utils.admin.mixins.super")
    def test_get_actions_with_delete_selected(self, mock_super):
        mock_super.return_value.get_actions.return_value = {
            "delete_selected": "delete_selected",
            "foo": "foo",
            "bar": "bar",
        }
        mock_request = Mock()
        result = self.mixin.get_actions(self.mixin(), request=mock_request)

        mock_super.return_value.get_actions.assert_called_once_with(
            mock_request
        )
        assert result == mock_super.return_value.get_actions.return_value

    @patch("utils.admin.mixins.super")
    def test_get_actions_without_delete_selected(self, mock_super):
        mock_super.return_value.get_actions.return_value = {
            "foo": "foo",
            "bar": "bar",
        }
        mock_request = Mock()
        result = self.mixin.get_actions(self.mixin(), request=mock_request)

        mock_super.return_value.get_actions.assert_called_once_with(
            mock_request
        )
        assert result == mock_super.return_value.get_actions.return_value
