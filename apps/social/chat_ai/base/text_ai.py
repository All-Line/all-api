from abc import ABC, abstractmethod


class TextAI(ABC):
    def __init__(self, pre_set: str, message: str = None):
        """
        :param pre_set: Pre Set of the text AI,
            like "You are a reporter who is trying to get a story"
        :param message: Message to be sent to the text AI
        """
        self.pre_set = pre_set
        self.message = message

    @abstractmethod
    def get_client(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_message(self, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _get_response(self, message):
        raise NotImplementedError  # pragma: no cover

    def get_response(self):
        message = self.get_message()
        response = self._get_response(message)
        return response
