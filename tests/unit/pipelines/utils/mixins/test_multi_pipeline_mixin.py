from pipelines.utils.mixins.multipipeline import MultiPipelineMixin


class TestMultiPipelineMixin:
    def test_get_pipeline(self):
        mixin = MultiPipelineMixin()
        mixin.action = "foo"
        mixin.pipeline = {"foo": "bar"}
        result = mixin.get_pipeline()

        assert result == "bar"
