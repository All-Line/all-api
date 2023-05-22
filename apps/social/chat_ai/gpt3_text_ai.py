from chatgptonic import ChatGPT
from decouple import config as env

from .base.text_ai import TextAI


class GPT3TextAI(TextAI):
    def get_client(self):
        return ChatGPT(env("OPEN_AI_KEY"))

    def get_message(self, *_args, **_kwargs):
        return f"""
            {self.pre_set}

            {self.message}
        """

    def _get_response(self, message):
        client = self.get_client()
        response = client.just_chat(message, 0.1)
        return response
