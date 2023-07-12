from enum import Enum


class ChatGPTModel(Enum):
    GPT_3_5 = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"

CHATGPT_ROLE_USER = "user"
CHATGPT_ROLE_SYSTEM = "system"
CHATGPT_ROLE_ASSISTANT = "assistant"

class ChatGPTParams:
    def __init__(self,
                 temperature: float | None = None,
                 presence_penalty: float | None = None,
                 frequency_penalty: float | None = None
                 ):
        self.temperature = temperature
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty

    def to_params(self)->dict:
        return {key:value for key, value in self.__dict__.items() if value is not None}


def make_chat_completion_message(message: str, role: str) -> dict:
    return {
        "content": message,
        "role": role
    }
