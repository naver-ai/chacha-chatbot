from enum import Enum
from typing import TypedDict, Optional


class ChatGPTModel(Enum):
    GPT_3_5 = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"


CHATGPT_ROLE_USER = "user"
CHATGPT_ROLE_SYSTEM = "system"
CHATGPT_ROLE_ASSISTANT = "assistant"
CHATGPT_ROLE_FUNCTION = "function"


class ChatGPTFunctionParameterProperty(TypedDict):
    type: str
    description: Optional[str]
    enum: Optional[list[str]]


class ChatGPTFunctionParameters(TypedDict):
    type: str
    properties: dict[str, ChatGPTFunctionParameterProperty]


class ChatGPTFunctionInfo(TypedDict):
    name: str
    description: Optional[str]
    parameters: ChatGPTFunctionParameters


class ChatGPTParams:
    def __init__(self,
                 temperature: float | None = None,
                 presence_penalty: float | None = None,
                 frequency_penalty: float | None = None,
                 functions: list[ChatGPTFunctionInfo] | None = None
                 ):
        self.temperature = temperature
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.functions = functions

    def to_params(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if value is not None}


def make_chat_completion_message(message: str, role: str, name: str = None) -> dict:
    result = {
        "content": message,
        "role": role
    }

    if name is not None and len(name) > 0:
        result["name"] = name

    return result