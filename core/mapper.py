from abc import ABC, abstractmethod
from typing import TypeVar, Generic, TypedDict

from core.chatbot import DialogTurn
from core.openai import ChatGPTModel

InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')
ParamsType = TypeVar('ParamsType')


class Mapper(Generic[InputType, OutputType, ParamsType], ABC):

    @abstractmethod
    async def run(self, input: InputType, params: ParamsType | None) -> OutputType:
        pass

class ChatGPTDialogSummarizerParams:

    def __init__(self, input_user_alias: str | None = None, input_system_alias: str | None = None):
        self.input_user_alias = input_user_alias
        self.input_system_alias = input_system_alias

class ChatGPTDialogSummarizer(Mapper[list[DialogTurn], str, ChatGPTDialogSummarizerParams]):

    def __init__(self,
                 model: str =ChatGPTModel.GPT_4.value,
                 gpt_params: dict | None = None):
        self.__model = model
        self.__gpt_params = dict()

    async def run(self, input: list[DialogTurn], params: ChatGPTDialogSummarizerParams | None) -> OutputType:
        pass