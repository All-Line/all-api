from unittest.mock import Mock, patch

from rest_framework import status
from rest_framework.viewsets import ViewSet

from pipelines.base import PipelineListViewSet, PipelineParamsViewSetMixin


class TestPipelineListViewSet:
    @classmethod
    def setup_class(cls):
        cls.viewset = PipelineListViewSet

    def test_parent(self):
        assert issubclass(PipelineListViewSet, ViewSet)
        assert issubclass(PipelineListViewSet, PipelineParamsViewSetMixin)

    @patch("pipelines.base.PipelineListViewSet.serializer")
    @patch("pipelines.base.PipelineListViewSet.get_pipeline")
    @patch("pipelines.base.PipelineListViewSet.get_pipeline_params")
    @patch("pipelines.base.Response")
    def test_list(
        self,
        mock_response,
        mock_get_pipeline_params,
        mock_get_pipeline,
        mock_serializer,
    ):
        request = Mock()
        mock_get_pipeline_params.return_value = {"foo": "bar"}
        viewset = self.viewset()
        result = viewset.list(request)

        mock_get_pipeline.assert_called_once()
        mock_get_pipeline_params.assert_called_once()
        mock_get_pipeline.return_value.assert_called_once_with(
            **mock_get_pipeline_params.return_value, request=request
        )
        mock_get_pipeline.return_value.return_value.run.assert_called_once()
        mock_serializer.assert_called_once_with(
            mock_get_pipeline.return_value.return_value.run.return_value, many=True
        )
        mock_response.assert_called_once_with(
            mock_serializer.return_value.data, status=status.HTTP_200_OK
        )
        assert result == mock_response.return_value
