from unittest.mock import Mock

from pipelines.base import BasePipeItem
from pipelines.items.add_mention_on_comment import AddMentionOnComment


class TestAddMentionOnComment:
    @classmethod
    def setup_class(cls):
        cls.item = AddMentionOnComment

    def test_parent_class(self):
        assert issubclass(self.item, BasePipeItem)

    def test_run(self):
        pipeline = Mock()
        item = self.item(pipeline)
        item._run()

        pipeline.comment.mentions.add.assert_called_once_with(pipeline.user)
        pipeline.comment.save.assert_called_once_with()
