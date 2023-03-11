from unittest.mock import Mock, patch

from pipelines.base import BasePipeItem
from pipelines.items import CreateUser


class TestCreateUser:
    @classmethod
    def setup_class(cls):
        cls.item = CreateUser

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    @patch("pipelines.items.create_user.UserModel")
    @patch("pipelines.items.create_user.CreateUser.log")
    def test_run(self, mock_log, mock_user_model):
        mock_pipeline = Mock()
        pipe_item = self.item(mock_pipeline)
        pipe_item._run()
        user = mock_user_model.objects.create.return_value

        mock_user_model.objects.create.assert_called_once_with(
            username=mock_pipeline.username,
            first_name=mock_pipeline.first_name,
            last_name=mock_pipeline.last_name,
            email=mock_pipeline.email,
            password=mock_pipeline.password,
            service=mock_pipeline.service,
            birth_date=mock_pipeline.birth_date,
            document=mock_pipeline.document,
            country=mock_pipeline.country,
            profile_image=mock_pipeline.profile_image,
        )
        mock_log.assert_called_once_with(
            f"A new user was created: {user.first_name} {user.last_name} ({user.id})"
        )
        assert mock_pipeline.user == user
