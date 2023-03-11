from unittest.mock import Mock, call, patch

from rest_framework import status
from rest_framework.viewsets import ViewSet

from pipelines.base import PipelineCreateViewSet, PipelineParamsViewSetMixin


class TestPipelineCreateViewSet:
    @classmethod
    def setup_class(cls):
        cls.viewset = PipelineCreateViewSet

    def test_parent(self):
        assert issubclass(PipelineCreateViewSet, ViewSet)
        assert issubclass(PipelineCreateViewSet, PipelineParamsViewSetMixin)

    @patch("pipelines.base.PipelineCreateViewSet.serializer")
    @patch("pipelines.base.PipelineCreateViewSet.get_pipeline")
    @patch("pipelines.base.PipelineCreateViewSet.get_pipeline_params")
    @patch("pipelines.base.Response")
    def test_create_serializable(
        self,
        mock_response,
        mock_get_pipeline_params,
        mock_get_pipeline,
        mock_serializer,
    ):
        request = Mock()
        mock_get_pipeline_params.return_value = {"foo": "bar"}
        viewset = self.viewset()
        result = viewset.create(request)

        mock_serializer.return_value.is_valid.assert_called_once_with(
            raise_exception=True
        )

        mock_get_pipeline.assert_called_once()
        mock_get_pipeline_params.assert_called_once()
        mock_get_pipeline.return_value.assert_called_once_with(
            **mock_get_pipeline_params.return_value, request=request
        )
        mock_get_pipeline.return_value.return_value.run.assert_called_once()
        assert mock_serializer.call_args_list == [
            call(data=request.data),
            call(mock_get_pipeline.return_value.return_value.run.return_value),
        ]
        mock_response.assert_called_once_with(
            mock_serializer.return_value.data, status=status.HTTP_201_CREATED
        )
        assert result == mock_response.return_value

    @patch("pipelines.base.PipelineCreateViewSet.serializer")
    @patch("pipelines.base.PipelineCreateViewSet.get_pipeline")
    @patch("pipelines.base.PipelineCreateViewSet.get_pipeline_params")
    @patch("pipelines.base.Response")
    def test_create_no_serializable(
        self,
        mock_response,
        mock_get_pipeline_params,
        mock_get_pipeline,
        mock_serializer,
    ):
        request = Mock()
        mock_get_pipeline_params.return_value = {"foo": "bar"}

        viewset = self.viewset()
        viewset.is_serializable = False

        result = viewset.create(request)
        mock_serializer.assert_called_once_with(data=request.data)
        mock_serializer.return_value.is_valid.assert_called_once_with(
            raise_exception=True
        )

        mock_get_pipeline.assert_called_once()
        mock_get_pipeline_params.assert_called_once()
        mock_get_pipeline.return_value.assert_called_once_with(
            **mock_get_pipeline_params.return_value, request=request
        )
        mock_get_pipeline.return_value.return_value.run.assert_called_once()
        mock_response.assert_called_once_with(status=status.HTTP_201_CREATED)
        assert result == mock_response.return_value
