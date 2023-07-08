from enum import Enum

from core.chatbot import DialogTurn, ResponseGenerator
from core.generators import ChatGPTResponseGenerator
from core.generators.state import StateBasedResponseGenerator, StateType


class EmotionChatbotPhase(Enum):
    Rapport = "rapport"


class EmotionChatbotResponseGenerator(StateBasedResponseGenerator[EmotionChatbotPhase]):

    async def get_generator(self, state: StateType, payload: dict | None) -> ResponseGenerator:
        # Get generator caches
        generator = self.__generators[state]

        if state == EmotionChatbotPhase.Rapport.value:
            await generator.initialize()
        # TODO: Iterate over other phase types...

        return generator

    def __init__(self, user_name: str):
        super().__init__(initial_state=EmotionChatbotPhase.Rapport)
        self.__generators: dict[EmotionChatbotPhase, ResponseGenerator] = dict()

        # TODO: Initialize generator instances
        self.__generators[EmotionChatbotPhase.Rapport] = ChatGPTResponseGenerator(
            base_instruction="You are an AI assistant who talks like a child aged around 10. You always speak in Korean.",
            initial_user_message=f"안녕! 내 이름은 {user_name}."
        )


    async def calc_next_state_info(self, current: str, dialog: list[DialogTurn]) -> tuple[str, dict | None] | None:
        if current == EmotionChatbotPhase.Rapport.value:
            # TODO check whether the child wants to share his/her emotion and return the next state accordingly..
            return None

        return None