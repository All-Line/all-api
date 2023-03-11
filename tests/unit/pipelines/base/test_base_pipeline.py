from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch
from uuid import UUID

import freezegun

from pipelines.base import BasePipeline
from pipelines.exceptions import StopPipelineException


class TestBasePipeline:
    def test_init(self):
        pipeline = BasePipeline([])

        assert pipeline.uuid is not None
        assert pipeline.date_init is not None
        assert pipeline.steps == []
        assert isinstance(pipeline.uuid, UUID)
        assert isinstance(pipeline.date_init, datetime)
        assert isinstance(pipeline.steps, list)

    @freezegun.freeze_time("2022-01-02 00:00:00")
    def test_get_runtime(self):
        pipeline = BasePipeline([])
        pipeline.date_init = pipeline.date_init - timedelta(days=1)
        result = pipeline.get_runtime()
        expected = str(datetime.now() - pipeline.date_init)

        assert result == expected

    @freezegun.freeze_time("2022-01-02 00:00:00")
    @patch("pipelines.base.logging")
    @patch("pipelines.base.get_class_name")
    def test_run_success(self, mock_get_class_name, mock_logging):
        mock_get_class_name.return_value = "BasePipeline"
        step_1 = Mock()
        step_2 = Mock()
        pipeline = BasePipeline([step_1, step_2])
        detach = 50 * "#"
        pipeline.run()

        mock_get_class_name.assert_called_once_with(BasePipeline)
        mock_logging.getLogger.assert_called_once_with("BasePipeline")
        step_1.assert_called_once_with(pipeline=pipeline)
        step_2.assert_called_once_with(pipeline=pipeline)
        step_1.return_value.run.assert_called_once()
        step_2.return_value.run.assert_called_once()
        logger = mock_logging.getLogger()
        assert logger.info.call_args_list == [
            call(f"\n {detach} \n"),
            call(f" \n Pipeline: BasePipeline (Pipeline ID = {pipeline.uuid}) \n"),
            call(f"Tempo de execução: {pipeline.get_runtime()}"),
            call(f"\n {detach} \n"),
        ]

    @freezegun.freeze_time("2022-01-02 00:00:00")
    @patch("pipelines.base.logging")
    @patch("pipelines.base.get_class_name")
    def test_run_failed(self, mock_get_class_name, mock_logging):
        mock_get_class_name.return_value = "BasePipeline"
        err = "Some Error"
        step_1 = Mock()
        step_2 = Mock()
        step_1.return_value.run.side_effect = StopPipelineException(err)
        pipeline = BasePipeline([step_1, step_2])
        detach = 50 * "#"
        pipeline.run()

        mock_get_class_name.assert_called_once_with(BasePipeline)
        mock_logging.getLogger.assert_called_once_with("BasePipeline")
        step_1.assert_called_once_with(pipeline=pipeline)
        step_2.assert_not_called()
        logger = mock_logging.getLogger()
        assert logger.info.call_args_list == [
            call(f"\n {detach} \n"),
            call(f" \n Pipeline: BasePipeline (Pipeline ID = {pipeline.uuid}) \n"),
            call(f"Tempo de execução: {pipeline.get_runtime()}"),
            call(f"\n {detach} \n"),
        ]
        logger.error.assert_called_once_with(f"\n {err} \n")
