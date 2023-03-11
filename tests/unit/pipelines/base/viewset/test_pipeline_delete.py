from unittest.mock import Mock, patch

from rest_framework import status
from rest_framework.viewsets import ViewSet

from pipelines.base import PipelineDeleteViewSet, PipelineParamsViewSetMixin


class TestPipelineDeleteViewSet:
    @classmethod
    def setup_class(cls):
        cls.viewset = PipelineDeleteViewSet

    def test_parent(self):
        assert issubclass(PipelineDeleteViewSet, ViewSet)
        assert issubclass(PipelineDeleteViewSet, PipelineParamsViewSetMixin)

    @patch("pipelines.base.PipelineDeleteViewSet.serializer")
    @patch("pipelines.base.PipelineDeleteViewSet.get_pipeline")
    @patch("pipelines.base.PipelineDeleteViewSet.get_pipeline_params")
    @patch("pipelines.base.Response")
    @patch("pipelines.base.getattr")
    def test_delete_without_pipeline_error_and_no_serializing(
        self,
        mock_getattr,
        mock_response,
        mock_get_pipeline_params,
        mock_get_pipeline,
        mock_serializer,
    ):
        request = Mock()
        mock_get_pipeline_params.return_value = {"foo": "bar"}
        mock_getattr.return_value = None
        viewset = self.viewset()
        viewset.serializer = None
        result = viewset.delete(request)

        mock_serializer.return_value.assert_not_called()
        mock_serializer.return_value.is_valid.assert_not_called()

        mock_get_pipeline.assert_called_once()
        mock_get_pipeline_params.assert_called_once()
        mock_get_pipeline.return_value.assert_called_once_with(
            **mock_get_pipeline_params.return_value, request=request
        )
        mock_get_pipeline.return_value.return_value.run.assert_called_once()
        mock_getattr.assert_called_once_with(
            mock_get_pipeline.return_value, "error", None
        )

        mock_response.assert_called_once_with(status=status.HTTP_204_NO_CONTENT)
        assert result == mock_response.return_value

    @patch("pipelines.base.PipelineDeleteViewSet.serializer")
    @patch("pipelines.base.PipelineDeleteViewSet.get_pipeline")
    @patch("pipelines.base.PipelineDeleteViewSet.get_pipeline_params")
    @patch("pipelines.base.Response")
    @patch("pipelines.base.getattr")
    def test_delete_with_pipeline_error_and_serializing(
        self,
        mock_getattr,
        mock_response,
        mock_get_pipeline_params,
        mock_get_pipeline,
        mock_serializer,
    ):
        request = Mock()
        mock_get_pipeline_params.return_value = {"foo": "bar"}
        mock_getattr.return_value = True
        viewset = self.viewset()
        result = viewset.delete(request)

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
        mock_getattr.assert_called_once_with(
            mock_get_pipeline.return_value, "error", None
        )

        mock_response.assert_called_once_with(
            {"detail": mock_get_pipeline.return_value.error},
            status=status.HTTP_404_NOT_FOUND,
        )
        assert result == mock_response.return_value
