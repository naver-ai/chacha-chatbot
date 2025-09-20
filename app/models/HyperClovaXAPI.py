from chatlib.chatbot import ChatCompletionResponseGenerator, ChatCompletionParams, TokenLimitExceedHandler
from chatlib.utils.integration import APIAuthorizationVariableSpecPresets, APIAuthorizationVariableSpec
from chatlib.llm.chat_completion_api import ChatCompletionAPI, ChatCompletionMessage, ChatCompletionMessageRole, ChatCompletionResult
from functools import cache
import aiohttp
from jinja2 import Template
from typing import Callable, Awaitable, Any, Optional
import re

class HyperClovaXAPI(ChatCompletionAPI):

    __host_spec = APIAuthorizationVariableSpecPresets.Host

    @classmethod
    @cache
    def provider_name(cls) -> str:
        return "HyperClovaX"
    
    @classmethod
    def get_auth_variable_specs(cls) -> list[APIAuthorizationVariableSpec]:
        return [cls.__host_spec]
    
    @classmethod
    def _authorize_impl(cls, variables):
        if variables.get(cls.__host_spec) is None:
            return False
        return True
    

    def _extract_message(self, text: str) -> str:
        # <|im_start|>assistant 와 <|im_end|> 사이의 내용을 잡아오기
        match = re.search(r"<\|im_start\|>assistant\n(.*?)<\|im_end\|>", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    

    async def _run_chat_completion_impl(self, model, messages, params) -> ChatCompletionResult:

        prompt = ""

        for message in messages:
            if message.role == ChatCompletionMessageRole.SYSTEM:
                prompt += f"<|im_start|>system\n{message.content}<|im_end|>\n"
            elif message.role == ChatCompletionMessageRole.USER:
                prompt += f"<|im_start|>user\n{message.content}<|im_end|>\n"
            elif message.role == ChatCompletionMessageRole.ASSISTANT:
                prompt += f"<|im_start|>assistant\n{message.content}<|im_end|>\n"

        headers = {
            "content-type": "application/json; charset=utf-8"
        }

        data = {
            "prompt": prompt,
            "temperature": params.get("temperature", 0.5),
            "max_tokens": params.get("max_tokens", 1000),
            "top_p": params.get("top_p", 0.6),
            "stop": [
                "<|stop|>",
                "<|endofturn|>"
            ],
            "include_probs": False,
            "repeatition_penalty": 1
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.get_auth_variable_for_spec(self.__host_spec), json=data, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get response from HyperClovaX API: {resp.status}, {await resp.text()}")
                result_json = await resp.json()
                # Assuming the response structure contains 'choices' similar to OpenAI
                if 'choices' in result_json and len(result_json['choices']) > 0:
                    message_content = self._extract_message(result_json['choices'][0].get('text', '').strip())

                    return ChatCompletionResult(
                        message=ChatCompletionMessage(
                            role=ChatCompletionMessageRole.ASSISTANT,
                            content=message_content
                        ),
                        finish_reason=result_json['choices'][0].get('finish_reason', 'stop'),
                        provider=self.provider_name(),
                        model=model,
                        prompt_tokens=0,  # HyperClovaX API may not provide this info
                        completion_tokens=len(message_content.split()),  # Rough estimate
                        total_tokens=len(message_content.split())  # Rough estimate
                    )
                return None


    def get_token_limit(self, model: str) -> int:
        return 120000
    
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

    def __init__(self, model: str = "hyperclova-x-large", base_instruction: str | Template | None = None,
                 instruction_parameters: dict | None = None,
                 initial_user_message: str | list[ChatCompletionMessage] | None = None,
                 chat_completion_params: ChatCompletionParams | None = None,
                 function_handler: Callable[[str, dict | None], Awaitable[any]] | None = None,
                 special_tokens: list[tuple[str, str, any]] | None = None, verbose: bool = False,
                 token_limit_exceed_handler: TokenLimitExceedHandler | None = None, token_limit_tolerance: int = 1024):
        super().__init__(self.get_api(), model, base_instruction, instruction_parameters, initial_user_message,
                         chat_completion_params, function_handler, special_tokens, verbose, token_limit_exceed_handler,
                         token_limit_tolerance)