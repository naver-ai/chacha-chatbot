from enum import Enum


class ChatGPTModel(Enum):
    GPT_3_5 = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"

CHATGPT_ROLE_USER = "user"
CHATGPT_ROLE_SYSTEM = "system"
CHATGPT_ROLE_ASSISTANT = "assistant"
