from enum import Enum

from core.chatbot import DialogTurn, ResponseGenerator
from core.generators import ChatGPTResponseGenerator
from core.generators.state import StateBasedResponseGenerator, StateType
import openai

class EmotionChatbotPhase(Enum):
    Rapport = "rapport"
    Label = "label"
    Find = "find"
    Record = "record"
    Share = "share"


class EmotionChatbotResponseGenerator(StateBasedResponseGenerator[EmotionChatbotPhase]):

    async def get_generator(self, state: StateType, payload: dict | None) -> ResponseGenerator:
        # Get generator caches
        generator = self.__generators[state]

        if state == EmotionChatbotPhase.Rapport.value:
            await generator.initialize()
        # TODO: Iterate over other phase types...

        return generator

    def __init__(self, user_name: str, user_age: int):
        super().__init__(initial_state=EmotionChatbotPhase.Rapport)
        self.__generators: dict[EmotionChatbotPhase, ResponseGenerator] = dict()

        # TODO: Initialize generator instances
        self.__generators[EmotionChatbotPhase.Rapport] = ChatGPTResponseGenerator(
            base_instruction=f"""
            Your role: You are a cheerful, friendly child.
            Your name is 챗봇 and {user_age} years old.
            After the introduction and greeting, build rapport with the user by asking about how the user’s day was. If the user answers they do not know, ask about their week. If the user answers they do not know again, ask about what fun activity they have done lately. To encourage the user to share their episode, share your fun or joyful episode. You can overwrite the 3-setnece speaking when sharing your episode.            
            Once they share their episode, ask more about it, such as what happened and who was involved. Then, ask the user how they feel by connecting to the episode.                     
            Continue the conversation until the user indicates he or she does not want to talk anymore. 
            If the user indicates he or she does not want to talk anymore, ask the user if he or she wants to talk later isntead.

            Speaking rules: 
            1. Use a simple, informal Korean, like talking to a peer friend. 
            2. Say three sentences at the most each time. 
            3. Ask one question per conversation turn. 
            4. You can say, "I don't know," and go back to the conversation topic if the user asks a question that should be asked to adults or unrelated to the conversation topic.
""",
            initial_user_message=f"안녕! 내 이름은 {user_name}라고 해. 난 {user_age}살이야"
        )

        self.__generators[EmotionChatbotPhase.Label] = ChatGPTResponseGenerator(
            base_instruction="""
            Based on the previous conversation history about the user’s interests, ask the user to elaborate more about their emotions and what makes him or her feel that way by providing them the 8 emotions. Give positive 4 emotions if they shared positive feelings, and negative 4 emotions if shaerd negative feeelings. 
            The emotions are based on Plutchik’s Wheel of Emotions: 
            1. Joy (기쁨)(긍정)
            2. Trust (신뢰)(긍정)
            3. Fear (두려움)(부정)
            4. Surprise (놀람)(긍정)
            5. Sadness (슬픔)(부정)
            6. Disgust (불쾌)(부정)
            7. Anger (화)(부정)
            8. Anticipation (기대)(긍정)

            Empathize the user's emotion by restating how they felt.
            

            Speaking rules: 
            1. Use a simple, informal Korean like talking to a peer friend. 
            2. Say three sentences at the most each time. 
            3. Ask one question per conversation turn. 
            4. You can say "I don't know" and return to the conversation topic if the user asks a question that should be asked to adults or unrelated to the conversation topic.
            
            Example:
            Assistant: How did you feel when your mom kept forcing you to study for mid-term exams? 1. Joy, 2. Trust, 3. Fear, 4. Surprise, 5. Sadness, 6. Disgust, 7. Anger, 8. Anticipation. 
            User: Angry and sad
            Assistant: You were angry and sad because your mom kept asking you why you were not studying. You must felf envy then.
""",
            initial_user_message="화가 나고 슬퍼."
        )



    async def calc_next_state_info(self, current: EmotionChatbotPhase, dialog: list[DialogTurn]) -> tuple[EmotionChatbotPhase, dict | None] | None:
        if current == EmotionChatbotPhase.Rapport :
            if len(dialog) > 0 :
                    phase_classifier = ChatGPTResponseGenerator(
                    base_instruction=f"""
                        Information about your role: You are a conversation analyst. 
                        Speaking rule: 
                        1) Say either "label" or "rapport"
                        2) Do not say or ask other words
                        Analyze the content of the conversation, you recommend the appropriate conversation phase for the next step. 
                        Currently the phase is Rapport. If you suggest to move on to the next phase, just return "label". Otherwise, reutrn "rapport"
                        1. Rapport: In the initial phase, you and the user establish a connection through casual conversation in 4~6 turns. 
                        2. Label: If the user has expressed a desire to talk about their emotions, you suggest a 'Label’ phase
                        """,
                    initial_user_message="Speaking rule: 1) Say either 'label' or 'rapport' 2) Do not say or ask other words",
                    temperature= 0.1
                   )
                    phase_suggestion = await phase_classifier.get_response(dialog)
                    # print(f"Phase suggestion: {phase_suggestion[0]}")      

                    if "label" in phase_suggestion[0]:
                        return EmotionChatbotPhase.Label, None
            else:
                return None


            # result = ChatGPTResponseGenerator(
            #     base_instruction=f"""
            #     Information about your role: You are a conversation analyst. 
            #     You summarize the content of the user’s conversation history. 
            #     After summarizing the content of the conversation, you recommend the appropriate conversation phase for the next step. 
            #     Currently the phase is Rapport. If you suggest to move on to the next phase, just return "label". Otherwise, reutrn "rapport"
            #     1. Rapport: In the initial phase, you and the user establish a connection through casual conversation in 4~6 turns. 
            #     2. Label: If the user has expressed a desire to talk about their emotions, you suggest a 'Label’ phase
            #     Output format: label
            #     """,
            #     initial_user_message= dialog
            # )