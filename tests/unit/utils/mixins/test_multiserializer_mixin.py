from utils.mixins.multiserializer import MultiSerializerMixin


class TestMultiSerializerMixin:
    def test_serializers(self):
        assert MultiSerializerMixin.serializers == {
            "default": None,
        }

    def test_get_serializer_class(self):
        mixin = MultiSerializerMixin()
        mixin.action = "foo"
        mixin.serializers = {"foo": "bar"}
        result = mixin.get_serializer_class()

        assert result == "bar"
