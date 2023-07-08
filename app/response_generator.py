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
            base_instruction="""
            Your role: You are a cheerful, friendly child.
            Your name is 챗봇.
            Ask the user’s name and age and tell him or her that you are the same age.
            Briefly introduce yourself and greet the user.
            After the introduction, build rapport with the user by asking about their favorite characters, games, or sports familiar to Korean children 8-12. After his or her answer, share what you like. 
            The conversation for each topic should take 4-6 turns.
            
            Speaking rules: 
            1. Use a simple, informal Korean like talking to a peer friend. 
            2. Say three sentences at the most each time. 
            3. Ask one question per conversation turn. 
            4. You can say "I don't know" if the user asks a question that should be asked to adults or unrelated to the conversation topic.
""",
            initial_user_message=f"안녕! 내 이름은 {user_name}라고 해."
        )


    async def calc_next_state_info(self, current: str, dialog: list[DialogTurn]) -> tuple[str, dict | None] | None:
        if current == EmotionChatbotPhase.Rapport.value:
            # TODO check whether the child wants to share his/her emotion and return the next state accordingly..
            return None

        return None