from unittest.mock import Mock, patch

from apps.buying.models import PackageModel
from apps.user.models import UserModel
from pipelines.base import BasePipeItem
from pipelines.items.create_contract import CreateContract


class TestSetUserPremium:
    @classmethod
    def setup_class(cls):
        cls.item = CreateContract

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    @patch("apps.buying.models.ContractModel.objects.create")
    def test_run(self, mock_create):
        user = UserModel()
        package = PackageModel()
        pipeline = Mock(user=user, package=package, receipt="receipt")
        item = self.item(pipeline)
        item._run()

        mock_create.assert_called_once_with(
            user=user, receipt="receipt", package=package
        )
