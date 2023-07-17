import json
from asyncio import to_thread
from typing import Awaitable, Any, Callable

import openai

from core.chatbot import ResponseGenerator, Dialogue
from core.openai_utils import ChatGPTModel, ChatGPTRole, \
    ChatGPTParams, \
    make_chat_completion_message


class ChatGPTResponseGenerator(ResponseGenerator):

    def __init__(self,
                 model: str = ChatGPTModel.GPT_4,
                 base_instruction: str | None = None,
                 instruction_parameters: dict | None = None,
                 initial_user_message: str | list[dict] | None = None,
                 params: ChatGPTParams | None = None,
                 function_handler: Callable[[str, dict | None], Awaitable[Any]] | None = None,
                 verbose: bool = False
                 ):

        self.model = model

        self.gpt_params = params or ChatGPTParams()

        self.initial_user_message = initial_user_message

        self.__base_instruction = base_instruction if base_instruction is not None else "You are a ChatGPT assistant that is empathetic and supportive."

        self.__instruction_parameters = instruction_parameters

        self.__resolve_instruction()

        self.function_handler = function_handler

        self.verbose = verbose

    def __resolve_instruction(self):
        if self.__instruction_parameters is not None:
            self.__instruction = self.__base_instruction.format(**self.__instruction_parameters)
        else:
            self.__instruction = self.__base_instruction

    def update_instruction_parameters(self, params: dict):
        if self.__instruction_parameters is not None:
            self.__instruction_parameters.update(params)
        else:
            self.__instruction_parameters = params
        self.__resolve_instruction()

    async def _get_response_impl(self, dialog: Dialogue) -> tuple[str, dict | None]:
        dialogue_converted = [
            make_chat_completion_message(turn.message, ChatGPTRole.USER if turn.is_user else ChatGPTRole.ASSISTANT)
            for turn in dialog]

        instruction = self.__instruction
        if instruction is not None:

            instruction_turn = make_chat_completion_message(instruction, ChatGPTRole.SYSTEM)

            messages = [instruction_turn]
            if self.initial_user_message is not None:
                if isinstance(self.initial_user_message, str):
                    messages.append(make_chat_completion_message(self.initial_user_message, ChatGPTRole.USER))
                else:
                    messages.extend(self.initial_user_message)

            messages.extend(dialogue_converted)
        else:
            messages = dialogue_converted

        result = await to_thread(openai.ChatCompletion.create,
                                 model=self.model,
                                 messages=messages,
                                 **self.gpt_params.to_params()
                                 )
        top_choice = result.choices[0]

        if top_choice.finish_reason == 'stop':
            response_text = top_choice.message.content
            return response_text, None
        elif top_choice.finish_reason == 'function_call':
            function_call_info = top_choice["message"]["function_call"]
            function_name = function_call_info["name"]
            function_args = json.loads(function_call_info["arguments"])

            if self.verbose: print(f"Call function - {function_name} ({function_args})")

            function_call_result = await self.function_handler(function_name, function_args)
            dialogue_with_func_result = dialogue_converted + [
                make_chat_completion_message(function_call_result, ChatGPTRole.FUNCTION, name=function_name)
            ]
            new_result = await to_thread(openai.ChatCompletion.create,
                                         model=self.model,
                                         messages=dialogue_with_func_result,
                                         **self.gpt_params.to_params()
                                         )
            top_choice = new_result.choices[0]
            if top_choice.finish_reason == 'stop':
                response_text = top_choice.message.content
                return response_text, None
            else:
                print("Shouldn't reach here")

        else:
            raise Exception(f"ChatGPT error - {top_choice.finish_reason}")

    def write_to_json(self, parcel: dict):
        parcel["model"] = self.model
        parcel["gpt_params"] = self.gpt_params.to_params()
        parcel["initial_user_message"] = self.initial_user_message
        parcel["base_instruction"] = self.__base_instruction
        parcel["instruction_parameters"] = self.__instruction_parameters
        parcel["verbose"] = self.verbose

    def restore_from_json(self, parcel: dict):
        self.model = parcel["model"]
        self.gpt_params = ChatGPTParams(**parcel["gpt_params"])
        self.initial_user_message = parcel["initial_user_message"]
        self.__base_instruction = parcel["base_instruction"]
        self.__instruction_parameters = parcel["instruction_parameters"]
        self.verbose = parcel["verbose"]
        self.__resolve_instruction()
