import json

from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator, StateType

from app.common import EmotionChatbotPhase
from app.phases import rapport, label, find, record, share
from chatlib.chatbot import ResponseGenerator, Dialogue
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTParams


class EmotionChatbotResponseGenerator(StateBasedResponseGenerator[EmotionChatbotPhase]):

    def __init__(self, user_name: str | None = None, user_age: int = None, verbose: bool = False):
        super().__init__(initial_state=EmotionChatbotPhase.Rapport, verbose=verbose)

        self.__user_name = user_name
        self.__user_age = user_age

        self.__generators: dict[EmotionChatbotPhase, ResponseGenerator] = dict()

        self.__generators[EmotionChatbotPhase.Rapport] = rapport.create_generator()
        self.__generators[EmotionChatbotPhase.Label] = label.create_generator()
        self.__generators[EmotionChatbotPhase.Find] = find.create_generator()
        self.__generators[EmotionChatbotPhase.Record] = record.create_generator()
        self.__generators[EmotionChatbotPhase.Share] = share.create_generator()

    def write_to_json(self, parcel: dict):
        super().write_to_json(parcel)
        parcel["user_name"] = self.__user_name
        parcel["user_age"] = self.__user_age

    def restore_from_json(self, parcel: dict):
        self.__user_name = parcel["user_name"]
        self.__user_age = parcel["user_age"]

        super().restore_from_json(parcel)

    async def get_generator(self, state: StateType, payload: dict | None) -> ResponseGenerator:
        # Get generator caches
        generator = self.__generators[state]

        if state == EmotionChatbotPhase.Rapport:
            if isinstance(generator, ChatGPTResponseGenerator):
                generator.update_instruction_parameters(dict(user_name = self.__user_name, user_age = self.__user_age))
        elif state == EmotionChatbotPhase.Label:
            if isinstance(generator, ChatGPTResponseGenerator):
                generator.update_instruction_parameters(payload)  # Put the result of rapport conversation
        elif state == EmotionChatbotPhase.Find:
            await generator.initialize()
        elif state == EmotionChatbotPhase.Record:
            await generator.initialize()
        elif state == EmotionChatbotPhase.Share:
            await generator.initialize()

        return generator

    async def calc_next_state_info(self, current: EmotionChatbotPhase, dialog: Dialogue) -> tuple[
                                                                                                EmotionChatbotPhase, dict | None] | None:
        # Rapport --> Label
        if current == EmotionChatbotPhase.Rapport:
            # Minimum 3 rapport building conversation turns
            if len(dialog) > 3:
                phase_suggestion = json.loads(await rapport.summarizer.run(dialog))
                print(phase_suggestion)
                # print(f"Phase suggestion: {phase_suggestion}")
                if "move_to_next" in phase_suggestion and phase_suggestion["move_to_next"] is True:
                    return EmotionChatbotPhase.Label, phase_suggestion
                else:
                    return None
        # Label --> Find OR Record
        elif current == EmotionChatbotPhase.Label:
            phase_suggestion = json.loads(await label.summarizer.run(dialog))
            print(phase_suggestion)
            if "next_phase" in phase_suggestion and isinstance(phase_suggestion["next_phase"], str):
                if phase_suggestion["next_phase"].lower() == "find":
                    return EmotionChatbotPhase.Find, phase_suggestion
                elif phase_suggestion["next_phase"].lower() == "record":
                    return EmotionChatbotPhase.Record, phase_suggestion
            else:
                return None

        # Find OR Record --> Share
        elif current == EmotionChatbotPhase.Find or current == EmotionChatbotPhase.Record:
            phase_classifier = ChatGPTDialogueSummarizer(
                base_instruction=f"""
                    Analyze the content of the conversation.
                    Determine whether it is reasonable to move on to the next conversation phase or not.

                    Rules:
                    1) Answer options: "Share", "Find", or "Record". 
                    2) If {current} is "Find", return "Share," only when the user found a solution. 
                    3) If {current} is "Record", return "Share," only when you made 3 conversation turns. 
                    """,
                gpt_params=ChatGPTParams(temperature=0.1)
            )
            phase_suggestion = (await phase_classifier.run(dialog)).lower()
            if "share" in phase_suggestion:
                return EmotionChatbotPhase.Share, None
            else:
                return None
        else:
            return None
