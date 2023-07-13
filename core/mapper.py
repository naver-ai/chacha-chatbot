from abc import ABC, abstractmethod
from typing import TypeVar, Generic, TypedDict

from core.chatbot import DialogTurn
from core.generators import ChatGPTResponseGenerator
from core.openai import ChatGPTModel, ChatGPTParams, CHATGPT_ROLE_SYSTEM, make_chat_completion_message, \
    CHATGPT_ROLE_USER

InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')
ParamsType = TypeVar('ParamsType')


class Mapper(Generic[InputType, OutputType, ParamsType], ABC):

    @abstractmethod
    async def run(self, input: InputType, params: ParamsType | None = None) -> OutputType:
        pass

class ChatGPTDialogSummarizerParams:

    def __init__(self,
                 input_user_alias: str | None = None,
                 input_system_alias: str | None = None,
                 ):
        self.input_user_alias = input_user_alias
        self.input_system_alias = input_system_alias

DEFAULT_USER_ALIAS = "<|User|>"
DEFAULT_SYSTEM_ALIAS = "<|Assistant|>"


ALIAS_SEP = ": "
TURN_SEP = "\n"

class ChatGPTDialogueSummarizer(Mapper[list[DialogTurn], str, ChatGPTDialogSummarizerParams]):

    def __init__(self,
                 base_instruction: str,
                 model: str =ChatGPTModel.GPT_4.value,
                 gpt_params: ChatGPTParams | None = None):
        self.__model = model
        self.__gpt_params = gpt_params or ChatGPTParams()

        self.base_instruction = base_instruction
        self.__generator = ChatGPTResponseGenerator(
            model = model,
            base_instruction=base_instruction,
            params=gpt_params
        )

    async def run(self, input: list[DialogTurn], params: ChatGPTDialogSummarizerParams | None = None) -> str:
        self.__generator.initial_user_message = ChatGPTDialogueSummarizer.__convert_dialogue_to_str(input, params)
        resp, _, _ = await self.__generator.get_response([])
        # print(resp)
        return resp

    @staticmethod
    def __convert_dialogue_to_str(dialogue: list[DialogTurn], params: ChatGPTDialogSummarizerParams | None = None)->str:

        user_alias = (params.input_user_alias if params is not None and params.input_user_alias is not None else DEFAULT_USER_ALIAS)
        system_alias = (params.input_system_alias if params is not None and params.input_system_alias is not None else DEFAULT_SYSTEM_ALIAS)

        return TURN_SEP.join([(user_alias if turn.is_user else system_alias) + ALIAS_SEP + turn.message for turn in dialogue])