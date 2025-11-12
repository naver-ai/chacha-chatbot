from chatlib.chatbot import ChatCompletionResponseGenerator, ChatCompletionParams, TokenLimitExceedHandler
from chatlib.llm.chat_completion_api import ChatCompletionMessage, ChatCompletionAPI, ChatCompletionMessageRole, ChatCompletionResult
from chatlib.utils.integration import APIAuthorizationVariableSpec, APIAuthorizationVariableSpecPresets
from jinja2 import Template
from typing import Callable, Awaitable
from enum import StrEnum
from functools import cache
import aiohttp

class HyperClovaXModel(StrEnum):
    HCX_007 = "HCX-007"
    HCX_009 = "HCX-009"

class HyperClovaXAPI(ChatCompletionAPI):

    __api_key_spec = APIAuthorizationVariableSpecPresets.ApiKey

    @classmethod
    @cache
    def provider_name(cls) -> str:
        return "HyperClovaX"
    
    @classmethod
    def get_auth_variable_specs(cls) -> list[APIAuthorizationVariableSpec]:
        return [cls.__api_key_spec]
    
    @classmethod
    def _authorize_impl(cls, variables):
        if variables.get(cls.__api_key_spec) is None:
            return False
        return True


    async def _run_chat_completion_impl(self, model, messages, params):

        url = f"https://clovastudio.stream.ntruss.com/v3/chat-completions/{model}"

        headers = {
            'Authorization': f"Bearer {self.get_auth_variable_for_spec(self.__api_key_spec)}",
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json'
        }

        input_messages = []
        for msg in messages:

            if msg.role == ChatCompletionMessageRole.SYSTEM and msg.name == 'example_user':
                input_messages.append({"role": "user", "content": msg.content})
            elif msg.role == ChatCompletionMessageRole.SYSTEM and msg.name == 'example_assistant':
                input_messages.append({"role": "assistant", "content": msg.content})
            else:
                input_messages.append({
                    "role": msg.role == ChatCompletionMessageRole.SYSTEM and "system" or
                            msg.role == ChatCompletionMessageRole.USER and "user" or
                            msg.role == ChatCompletionMessageRole.ASSISTANT and "assistant",
                    "content": msg.content
                })

        async with aiohttp.ClientSession() as session:

            async with session.post(url, headers=headers, json={"messages": input_messages, "params": params}) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get response from HyperClovaX API: {resp.status}, {await resp.text()}")
                result_json = await resp.json()
                result = result_json['result']
                return ChatCompletionResult(
                    message=ChatCompletionMessage(
                        content=result['message']['content'],
                        role=ChatCompletionMessageRole.ASSISTANT
                    ),
                    finish_reason=result['finishReason'],
                    provider=self.provider_name(),
                    model=model,
                    prompt_tokens=result['usage']['promptTokens'],
                    completion_tokens=result['usage']['completionTokens'],
                    total_tokens=result['usage']['totalTokens']
                )

    def get_token_limit(self, model: str) -> int:
        return 128000
    
    def is_messages_within_token_limit(self, messages: list[ChatCompletionMessage], model: str, tolerance: int = 120) -> bool:
        # Simple token limit check based on message count
        # This is a placeholder; actual implementation should calculate token usage
        return len(messages) < (self.get_token_limit(model) - tolerance) // 50  # Assuming average 50 tokens per message
    
    def count_token_in_messages(self, messages: list[ChatCompletionMessage], model: str) -> int:
        # Simple token count based on message count
        # This is a placeholder; actual implementation should calculate token usage
        return len(messages) * 50  # Assuming average 50 tokens per message


class HyperClovaXResponseGenerator(ChatCompletionResponseGenerator):
    @classmethod
    @cache
    def get_api(cls) -> HyperClovaXAPI:
        return HyperClovaXAPI()

    def __init__(self, model: str = HyperClovaXModel.HCX_007, base_instruction: str | Template | None = None,
                 instruction_parameters: dict | None = None,
                 initial_user_message: str | list[ChatCompletionMessage] | None = None,
                 chat_completion_params: ChatCompletionParams | None = None,
                 function_handler: Callable[[str, dict | None], Awaitable[any]] | None = None,
                 special_tokens: list[tuple[str, str, any]] | None = None, verbose: bool = False,
                 token_limit_exceed_handler: TokenLimitExceedHandler | None = None, token_limit_tolerance: int = 1024):
        super().__init__(self.get_api(), model, base_instruction, instruction_parameters, initial_user_message,
                         chat_completion_params, function_handler, special_tokens, verbose, token_limit_exceed_handler,
                         token_limit_tolerance)