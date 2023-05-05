from apps.social.chat_ai.dummy_text_ai import DummyTextAI
from apps.social.chat_ai.gpt3_text_ai import GPT3TextAI

TEXT_AI = {
    "dummy": DummyTextAI,
    "gpt-3": GPT3TextAI,
}
