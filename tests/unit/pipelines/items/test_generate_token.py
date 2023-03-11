from unittest.mock import Mock, patch

from pipelines.base import BasePipeItem
from pipelines.items import GenerateToken


class TestGenerateToken:
    @classmethod
    def setup_class(cls):
        cls.item = GenerateToken

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    @patch("pipelines.items.generate_token.Token")
    def test_generate_random_username_successfully(self, mock_token):
        pipeline = Mock()
        item = self.item(pipeline)
        item._run()

        mock_token.objects.get_or_create.assert_called_once_with(user=pipeline.user)
