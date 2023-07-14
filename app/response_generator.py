import json
from enum import Enum

from core.chatbot import DialogueTurn, ResponseGenerator, Dialogue
from core.generators import ChatGPTResponseGenerator
from core.generators.state import StateBasedResponseGenerator, StateType
import openai

from core.mapper import ChatGPTDialogueSummarizer
from core.openai import ChatGPTParams, make_chat_completion_message, ChatGPTModel


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
        elif state == EmotionChatbotPhase.Label.value:
            await generator.initialize()
        elif state == EmotionChatbotPhase.Find.value:
            await generator.initialize()
        elif state == EmotionChatbotPhase.Record.value:
            await generator.initialize()
        elif state == EmotionChatbotPhase.Share.value:
            await generator.initialize()

        return generator

    def __init__(self, user_name: str, user_age: int):
        super().__init__(initial_state=EmotionChatbotPhase.Rapport)
        self.__generators: dict[EmotionChatbotPhase, ResponseGenerator] = dict()

        # Phase[Rapport]
        # Build rapport with the user. Ask about the most memorable episode. Ask about what happened and what the user felt.
        self.__generators[EmotionChatbotPhase.Rapport] = ChatGPTResponseGenerator(
            base_instruction=f"""
            Your role: You are a cheerful, friendly child. You like talking with friends.
            Your name is 챗봇, and {user_age} years old.
                        
            Your task: Complete the following two tasks.
            Remember to ask only one question per each conversation turn.
            For each conversation turn, execute one task only.
                        
            [Intro Task]
            Introduce yourself since it is your first time to meet the user.
            Explain who you are and share your interests and stories.
            Ask the user to introduce himself or herself.
            After his or her introduction, continue the conversation about the ongoing topic.
            Iterate such conversation about various topics.
            When at least 2 conversations are done, tell them you want to learn more about how his or her day is going.
            Continue the conversation about various topics until you find common ground and build rapport with the user.
            Once you build enough rapport with the user by learning more about what they did and who they are, move smoothly on to the next task if you build enough rapport with the user.
                        
            [Ask Task]
            Ask the user about an event that is the most memorable to him or her.
            If he or she does not remember or know what to say, ask them about an event when he or she enjoyed it or felt good or bad.
            Continue the conversation until the user indicates he or she does not want to talk about the specific topic anymore.
            If the user indicates he or she does not want to talk anymore, ask the user about other topics.
            If the user indicates he or she does not want to talk about anything, ask the user if he or she wants to talk later instead.

            Speaking rules: 
            1. Use a simple, informal Korean, like talking to a peer friend. 
            2. Ask one question per conversation turn. 
            3. Say three sentences at the most each time. 
            4. You can say, "I don't know," and go back to the conversation topic if the user asks a question that should be asked to adults or unrelated to the conversation topic.
""",
            initial_user_message=f"안녕! 내 이름은 {user_name}라고 해. 난 {user_age}살이야"
        )

        # Phase[Label]
        # Help the user label their emotion based on the Wheel of Emotions. Empathize their emotion.
        self.__generators[EmotionChatbotPhase.Label] = ChatGPTResponseGenerator(
            base_instruction="""
            Based on the previous conversation history about the user’s interests, ask the user to elaborate more about their emotions and what makes him or her feel that way by providing them the 8 emotions. 
            Give positive 4 emotions if they shared positive feelings, and negative 4 emotions if shared negative feelings. 
            Tell the user that they can pick one or two emotions. 
            The emotions are based on Plutchik’s Wheel of Emotions: 
            1. 기쁨 (긍정)
            2. 신뢰 (긍정)
            3. 두려움 (부정)
            4. 놀람 (긍정)
            5. 슬픔 (부정)
            6. 불쾌 (부정)
            7. 화 (부정)
            8. 기대 (긍정)

            Empathize the user's emotion by restating how they felt.
            If the user picks two emotions, explain about the combination emotions.
            1. 기대 + 기쁨 = 낙관
            2. 기쁨 + 신뢰 = 사랑
            3. 신뢰 + 두려움 = 굴복
            4. 두려움 + 놀람 = 경외감
            5. 놀람 + 슬픔 = 못 마땅함
            6. 슬픔 + 불쾌 = 후회
            7. 불쾌 + 화 = 경멸
            8. 화 + 기대 = 공격성   
            9. 기쁨 + 두려움 = 죄책감
            10. 두려움 + 슬픔 = 절망
            11. 슬픔 + 화 = 질투
            12. 화 + 기쁨 = 자부심
            13. 신뢰 + 놀람 = 호기심
            14. 놀람 + 불쾌 = 불신
            15. 불쾌 + 기대 = 냉소
            16. 기대 + 신뢰 = 희망
            17. 기쁨 + 놀람 = 큰 기쁨 (환희)
            18. 놀람 + 화 = 격분
            19. 화 + 신뢰 = 우월감
            20. 신뢰 + 슬픔 = 감상적
            21. 슬픔 + 기대 = 비관
            22. 기대 + 두려움 = 불안
            23. 두려움 + 불쾌 = 수치심
            24. 불쾌 + 기쁨 = 소름끼침         
            
            Speaking rules: 
            1. Use a simple, informal Korean like talking to a peer friend. 
            2. Say three sentences at the most each time. 
            3. Ask one question per conversation turn. 
            4. You can say "I don't know" and return to the conversation topic if the user asks a question that should be asked to adults or unrelated to the conversation topic.
            
            Example:
            <Child> 어제 학교 쉬는 시간이 낮잠을 자는데 친구가 갑자기 큰 소리를 내서 잠을 못 잤어.  
            <Chatbot> 그랬구나. 그때 기분이 어땠어?            
            <Child> 그냥 기분이 안 좋았어
            <Chatbot> 어떤 기분이 들었는지 자세히 말해줄 수 있을까?       
            <Child> 갑자기 소리를 내서 놀랐고, 화도 났어 
            <Chatbot> 그랬구나 갑자기 소리내서 놀랐고 화도 냈구나. 그걸 격분하다 또는 매우 화가 많이 났다고 표현해. 
            <Child>  격분이 뭐야?
        """
        )

        # Phase[Find]
        # Help the user find solution to the situation in which they felt negative emotions.
        self.__generators[EmotionChatbotPhase.Find] = ChatGPTResponseGenerator(
            base_instruction="""
                    Based on the previous conversation history about the user’s interests, ask the user about potential solutions to the problem.
                    If the episode involves other people, ask the user how they would feel. 
                    Help the user to find an actionable solution. 
         
                    Speaking rules: 
                    1. Use a simple, informal Korean like talking to a peer friend. 
                    2. Say three sentences at the most each time. 
                    3. Ask one question per conversation turn. 
                    4. You can say "I don't know" and return to the conversation topic if the user asks a question that should be asked to adults or unrelated to the conversation topic.
                """
        )

        # Phase[Record]
        # Encourage the user to record the moments in which they felt positive emotions.
        self.__generators[EmotionChatbotPhase.Record] = ChatGPTResponseGenerator(
            base_instruction="""
                    Based on the previous conversation history about the user’s interests, encourage the user to record the moments in which they felt positive emotions. 
                    Explain why it is important to record such moments.

                    Speaking rules: 
                    1. Use a simple, informal Korean like talking to a peer friend. 
                    2. Say three sentences at the most each time. 
                    3. Ask one question per conversation turn. 
                    4. You can say "I don't know" and return to the conversation topic if the user asks a question that should be asked to adults or unrelated to the conversation topic.
                """
        )

        # Phase[Share]
        # Encourage the user to share their emotion and the episode with their parents. Ask if they want to talk about other episodes.
        self.__generators[EmotionChatbotPhase.Share] = ChatGPTResponseGenerator(
            base_instruction="""
                    Based on the previous conversation history about the user’s interests, ask the user if they have already shared their emotions and the episode with their parents. 
                    If not, explain why it is important to share with them and encourage sharing.
                    If yes, praise them and ask what happened after sharing.

                    Speaking rules: 
                    1. Use a simple, informal Korean like talking to a peer friend. 
                    2. Say three sentences at the most each time. 
                    3. Ask one question per conversation turn. 
                    4. You can say "I don't know" and return to the conversation topic if the user asks a question that should be asked to adults or unrelated to the conversation topic.
                """
        )

    async def calc_next_state_info(self, current: EmotionChatbotPhase, dialog: Dialogue) -> tuple[EmotionChatbotPhase, dict | None] | None:
        # Rapport --> Label
        if current == EmotionChatbotPhase.Rapport:
            # Minimum 3 rapport building conversation turns
            if len(dialog) > 3:
                phase_classifier = ChatGPTDialogueSummarizer(
                    base_instruction=f"""
                        - You are a helpful assistant that analyzes the content of the dialog history.
                        - Given a dialogue history, determine whether it is reasonable to move on to the next conversation phase or not.
                        - Move to the next phase only when the user explicitly expressed their feelings (e.g., good or bad) and shared a specific episode that is the cause of the feelings.
                        - Use JSON format with the following properties:
                          (1) key_episode: a key episode that the user described.
                          (2) user_emotion: the emotion of the user caused by the key episode.
                          (3) move_to_next: A boolean whether it is reasonable to move on to the next conversation phase or not, judged based on (1) and (2).
                          (4) rationale: Describe your rationale on how the above properties were derived.
                        Refer to the example below.
                    """,
                    examples=[(
                        [
                            DialogueTurn("어제 친구랑 싸웠어", is_user=True),
                            DialogueTurn("친구랑 싸웠구나. 그때 기분이 어땠어?", is_user=False),
                            DialogueTurn("그냥 기분이 안 좋았어", is_user=True)
                        ],
                        json.dumps({
                            'key_episode': 'fighting with a friend',
                            'user_emotion': 'felt not good',
                            'move_to_next': True,
                            'rationale': "We can proceed to the next phase since the key episode and user's emotion are identified."
                        })
                    )],
                    gpt_params=ChatGPTParams(temperature=0.1)
                )
                phase_suggestion = json.loads(await phase_classifier.run(dialog))
                print(phase_suggestion)
                # print(f"Phase suggestion: {phase_suggestion}")
                if "move_to_next" in phase_suggestion and phase_suggestion["move_to_next"] is True :
                    return EmotionChatbotPhase.Label, {"classification_result": phase_suggestion}
                else:
                    return None
        # Label --> Find OR Record
        elif current == EmotionChatbotPhase.Label:
            phase_classifier = ChatGPTDialogueSummarizer(
                base_instruction=f"""
                    Analyze the content of the conversation.
                    Determine whether it is reasonable to move on to the next conversation phase or not.
                    Refer to the example.        

                    Rules:
                    1) Answer options: "Label", "Find", or "Record".
                    2) Return "Find," only when the following conditions are satisfied:
                        - The user expressed negative emotions and shared a specific episode that describes problems that the user faced.
                        - You empathized the user's negative emotion
                        - You explained the emotion to the user so that the user understand what emotion they felt.
                    3) Return "Record," only when the following conditions are satisfied:
                        - The user expressed positive emotions and shared a specific episode when they felt the emotions.
                        - You empathized the user's positive emotion. 
                        - You explained the emotion to the user so that the user understand what emotion they felt.
                    
                    [Example]
                    <Child> 어제 학교 쉬는 시간이 낮잠을 자는데 친구가 갑자기 큰 소리를 내서 잠을 못 잤어.  
                    <Chatbot> 그랬구나. 그때 기분이 어땠어?            
                    <Child> 그냥 기분이 안 좋았어
                    <Chatbot> 어떤 기분이 들었는지 자세히 말해줄 수 있을까?       
                    <Child> 갑자기 소리를 내서 놀랐고, 화도 났어 
                    <Chatbot> 그랬구나 갑자기 소리내서 놀랐고 화도 냈구나. 그걸 격분하다 또는 매우 화가 많이 났다고 표현해. 
                    <Child>  격분이 뭐야?
                    System: "Find" since the Chatbot empathized and explained the user's negative emotions and the key episode (a friend made a big noise while sleeping) and user's negative emotion (격분) is identified.
                    
                    <Child> 어제 친구들이랑 축구를 했어.  
                    <Chatbot> 축구를 했구나! 기분이 어땠어?            
                    <Child> 오랜만에 하는거라 기분이 좋았어
                    <Chatbot> 어떤 기분이 들었는지 자세히 말해줄 수 있을까?       
                    <Child> 뭔가 기대 됐고 기뻤어
                    <Chatbot> 오랜만에 친구들이랑 축구를 해서 기대가 되고 기뻤구나. 그걸 낙관적이라고 표현해. 
                    <Child>  낙관이 뭐야?
                    System: "Record" since the Chatbot empathized and explained the user's positive emotions and the key episode (playing soccer with friends) and user's positive emotion (낙관) is identified.
                    
                    """,
                gpt_params=ChatGPTParams(temperature=0.5)
            )
            phase_suggestion = (await phase_classifier.run(dialog)).lower()
            if "find" in phase_suggestion:
                return EmotionChatbotPhase.Find, None
            elif "record" in phase_suggestion:
                return EmotionChatbotPhase.Record, None
            else:
                return None

        # Find OR Record --> Share
        elif current == EmotionChatbotPhase.Find or current == EmotionChatbotPhase.Record :
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