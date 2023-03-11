from unittest.mock import Mock

from pipelines.base import BasePipeItem
from pipelines.items.set_user_premium import SetUserPremium


class TestSetUserPremium:
    @classmethod
    def setup_class(cls):
        cls.item = SetUserPremium

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    def test_run(self):
        user = Mock()
        pipeline = Mock(user=user)
        item = self.item(pipeline)
        item._run()

        user.save.assert_called_once()
        assert user.is_premium is True
