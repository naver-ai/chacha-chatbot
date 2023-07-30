from chatlib import dict_utils
from chatlib.chatbot import ResponseGenerator, Dialogue
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator, StateType
from chatlib.mapper import ChatGPTDialogSummarizerParams

from app.common import EmotionChatbotPhase
from app.phases import rapport, label, find, record, share


class EmotionChatbotResponseGenerator(StateBasedResponseGenerator[EmotionChatbotPhase]):

    def __init__(self, user_name: str | None = None, user_age: int = None, verbose: bool = False):
        super().__init__(initial_state=EmotionChatbotPhase.Rapport, verbose=verbose)

        self.__user_name = user_name
        self.__user_age = user_age

        self.__generators: dict[EmotionChatbotPhase, ChatGPTResponseGenerator] = dict()

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
            generator.update_instruction_parameters(dict(user_name=self.__user_name, user_age=self.__user_age))
        elif state == EmotionChatbotPhase.Label:
            generator.update_instruction_parameters(payload)  # Put the result of rapport conversation
        elif state in [EmotionChatbotPhase.Find, EmotionChatbotPhase.Share, EmotionChatbotPhase.Record]:
            generator.update_instruction_parameters(
                dict(key_episode=self._get_memoized_payload(EmotionChatbotPhase.Rapport)["key_episode"],
                     identified_emotion_types=", ".join(
                         self._get_memoized_payload(EmotionChatbotPhase.Label)["identified_emotion_types"]))
            )
        return generator

    async def calc_next_state_info(self, current: EmotionChatbotPhase, dialog: Dialogue) -> tuple[
                                                                                                EmotionChatbotPhase, dict | None] | None:
        # Rapport --> Label
        if current == EmotionChatbotPhase.Rapport:
            # Minimum 3 rapport building conversation turns
            if len(dialog) > 3:
                phase_suggestion = await rapport.summarizer.run(dialog)
                print(phase_suggestion)
                # print(f"Phase suggestion: {phase_suggestion}")
                if "move_to_next" in phase_suggestion and phase_suggestion["move_to_next"] is True:
                    return EmotionChatbotPhase.Label, phase_suggestion
                else:
                    return None
        # Label --> Find OR Record
        elif current == EmotionChatbotPhase.Label:
            phase_suggestion = await label.summarizer.run(dialog)
            print(phase_suggestion)
            next_phase = dict_utils.get_nested_value(phase_suggestion, "next_phase")
            if next_phase == "find":
                return EmotionChatbotPhase.Find, phase_suggestion
            elif next_phase == "record":
                return EmotionChatbotPhase.Record, phase_suggestion
            else:
                return None
        # Find/Record --> Share
        elif current == EmotionChatbotPhase.Find or current == EmotionChatbotPhase.Record:
            if current == EmotionChatbotPhase.Record:
                turns = [turn for turn in dialog if dict_utils.get_nested_value(turn.metadata, "state") == EmotionChatbotPhase.Record and turn.is_user == False]
                if len(turns) < 2:
                    print("Not enough turns to finish the Record phase. Continue.")
                    return None

            summarizer = find.summarizer if current == EmotionChatbotPhase.Find else record.summarizer
            phase_suggestion = await summarizer.run(dialog,
                                                    ChatGPTDialogSummarizerParams(
                                                        instruction_params=dict(
                                                            key_episode=
                                                            self._get_memoized_payload(EmotionChatbotPhase.Rapport)[
                                                                "key_episode"],
                                                            identified_emotion_types=", ".join(
                                                                self._get_memoized_payload(EmotionChatbotPhase.Label)[
                                                                    "identified_emotion_types"]))))
            print(phase_suggestion)
            if dict_utils.get_nested_value(phase_suggestion, "proceed_to_next_phase") is True:
                return EmotionChatbotPhase.Share, phase_suggestion
            else:
                return None
        # Share --> Rapport or Terminate
        elif current == EmotionChatbotPhase.Share:
            user_intention_to_share_new_episode = await share.check_new_episode_requested(dialog)
            if user_intention_to_share_new_episode:
                return EmotionChatbotPhase.Rapport, None
        return None
