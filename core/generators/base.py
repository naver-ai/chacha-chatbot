from asyncio import to_thread

import openai

from core.chatbot import ResponseGenerator, Dialogue
from core.openai import ChatGPTModel, CHATGPT_ROLE_USER, CHATGPT_ROLE_SYSTEM, CHATGPT_ROLE_ASSISTANT, ChatGPTParams, \
    make_chat_completion_message


class ChatGPTResponseGenerator(ResponseGenerator):

    def __init__(self,
                 model: str = ChatGPTModel.GPT_4.value,
                 base_instruction: str | None = None,
                 initial_user_message: str | list[dict] | None = None,
                 params: ChatGPTParams | None = None
                 ):

        self.model = model

        self.gpt_params = params or ChatGPTParams()

        self.initial_user_message = initial_user_message

        self.base_instruction = base_instruction if base_instruction is not None else "You are a ChatGPT assistant that is empathetic and supportive."

    def get_instruction(self) -> str | None:
        return self.base_instruction

    async def _get_response_impl(self, dialog: Dialogue) -> tuple[str, dict | None]:
        dialogue_converted = [
            make_chat_completion_message(turn.message, CHATGPT_ROLE_USER if turn.is_user else CHATGPT_ROLE_ASSISTANT)
            for turn in dialog]

        instruction = self.get_instruction()
        if instruction is not None:

            instruction_turn = make_chat_completion_message(instruction, CHATGPT_ROLE_SYSTEM)

            messages = [instruction_turn]
            if self.initial_user_message is not None:
                if isinstance(self.initial_user_message, str):
                    messages.append(make_chat_completion_message(self.initial_user_message, CHATGPT_ROLE_USER))
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
        else:
            raise Exception(f"ChatGPT error - {top_choice.finish_reason}")
