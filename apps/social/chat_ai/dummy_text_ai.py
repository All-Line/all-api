from .base.text_ai import TextAI


class DummyClient:
    def __init__(self, dummy_key):
        self.dummy_key = dummy_key

    def send(self, message):
        if self.dummy_key != "valid_dummy_test":
            raise ValueError("Invalid key")

        return f"Dummy response for {message}"


class DummyTextAI(TextAI):
    def __init__(self, pre_set: str = "You are Dummy Tester", message: str = None):
        super().__init__(pre_set, message)

    def get_client(self):
        return DummyClient("valid_dummy_test")

    def get_message(self, *args, **kwargs):
        return "Dummy test"

    def _get_response(self, message):
        client = self.get_client()
        response = client.send(message)
        return response
