from pipelines.base import PipelineParamsViewSetMixin


class TestPipelineParamsViewSetMixin:
    @classmethod
    def setup_class(cls):
        cls.mixin = PipelineParamsViewSetMixin()

    def test_attributes(self):
        assert self.mixin.serializer is None
        assert self.mixin.pipeline is None
        assert self.mixin.pipeline_params == {}
        assert self.mixin.is_serializable is True

    def test_get_pipeline(self):
        result = self.mixin.get_pipeline()

        assert result == self.mixin.pipeline

    def test_get_pipeline_params(self):
        result = self.mixin.get_pipeline_params()

        assert result == self.mixin.pipeline_params
