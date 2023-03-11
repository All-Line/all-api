class MultiSerializerMixin:
    serializers = {
        "default": None,
    }

    def get_serializer_class(self):
        return self.serializers[self.action]
