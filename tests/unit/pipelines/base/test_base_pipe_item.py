from unittest.mock import Mock, patch

import pytest

from pipelines.base import BasePipeItem


class TestBasePipeItem:
    def test_init(self):
        pipeline = Mock()
        item = BasePipeItem(pipeline=pipeline)

        assert item.pipeline == pipeline

    def test__run(self):
        pipeline = Mock()
        item = BasePipeItem(pipeline=pipeline)

        with pytest.raises(NotImplementedError):
            item._run()

    def test_get_pipeline_user_without_user(self):
        pipeline = Mock(user=None)
        item = BasePipeItem(pipeline=pipeline)
        result = item._get_pipeline_user()

        assert result is None

    def test_get_pipeline_user_with_user(self):
        pipeline = Mock(user="user-foo")
        item = BasePipeItem(pipeline=pipeline)
        result = item._get_pipeline_user()

        assert result == "user-foo"

    @patch("pipelines.base.logging")
    @patch("pipelines.base.get_class_name")
    def test_log(self, mock_get_class_name, mock_logging):
        mock_get_class_name.return_value = "BasePipeItem"
        pipeline = Mock()
        item = BasePipeItem(pipeline=pipeline)
        log = "test"
        detach_left = 10 * ">"
        detach_right = 10 * "<"
        item.log(log)

        mock_logging.getLogger.assert_called_once_with("BasePipeItem")
        mock_logging.getLogger.return_value.info.assert_called_once_with(
            f"{detach_left}{log}{detach_right} \n"
        )
        mock_get_class_name.assert_called_once_with(BasePipeItem)

    @patch("pipelines.base.BasePipeItem._run")
    def test_run(self, mock_run):
        pipeline = Mock()
        item = BasePipeItem(pipeline)
        item.run()

        mock_run.assert_called()
