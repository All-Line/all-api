from unittest.mock import Mock, patch

from pipelines.base import BasePipeItem
from pipelines.items import GenerateRandomUsername


class TestGenerateRandomUsername:
    @classmethod
    def setup_class(cls):
        cls.item = GenerateRandomUsername

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    @patch("pipelines.items.generate_random_username.UserModel")
    @patch("pipelines.items.generate_random_username.randint", return_value=1)
    def test_generate_random_username_successfully(self, mock_randint, mock_user_model):
        pipeline = Mock(service=Mock(slug="some_slug"))
        item = self.item(pipeline)

        username = "some_slug-1111"

        mock_user_model.DoesNotExist = Exception
        mock_user_model.objects.get.side_effect = Exception()

        response = item._generate_random_username()

        mock_user_model.objects.get.assert_called_once_with(username=username)
        assert response == username
        assert mock_randint.call_count == 4

    @patch(
        "pipelines.items.generate_random_username"
        ".GenerateRandomUsername._generate_random_username"
    )
    def test_run(self, mock_generate_random_username):
        pipeline = Mock(username=None)
        item = self.item(pipeline)
        item._run()

        mock_generate_random_username.assert_called_once()
        assert pipeline.username == mock_generate_random_username.return_value
