import json

from app.common import stringify_list, COMMON_SPEAKING_RULES
from core.chatbot import DialogueTurn
from core.generators import ChatGPTResponseGenerator


# Help the user label their emotion based on the Wheel of Emotions. Empathize their emotion.
from core.mapper import ChatGPTDialogueSummarizer
from core.openai_utils import ChatGPTParams


def create_generator():
    return ChatGPTResponseGenerator(
            base_instruction=f"""
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
            {stringify_list(COMMON_SPEAKING_RULES, ordered=True)}
            
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


classifier = ChatGPTDialogueSummarizer(
                base_instruction=f"""
                    - You are a helpful assistant that analyzes the content of the conversation.
                    - Determine whether it is reasonable to move on to the next conversation phase or not.
                    - Return JSON in the following format:
                        {{
                         "assistant_emphasized": boolean,
                         "assistant_explained": boolean,
                         "emotion_category": "positive" | "negative",
                         "identified_emotion_types": Array<string>,
                         "next_phase": "find" | "label" | null
                        }}
                
                    Rules for the "next_phase":
                    1) Set "find" only when the following conditions are satisfied:
                        - The user expressed negative emotions and shared a specific episode that describes problems that the user faced.
                        - You empathized the user's negative emotion
                        - You explained the emotion to the user so that the user understand what emotion they felt.
                    2) Set "record" only when the following conditions are satisfied:
                        - The user expressed positive emotions and shared a specific episode when they felt the emotions.
                        - You empathized the user's positive emotion. 
                        - You explained the emotion to the user so that the user understand what emotion they felt.
                    3) Set null if it is better to stay in the current conversational phase.
                    
                    Refer to the examples below.
                        """,

                examples=[
                    ([
                         DialogueTurn("어제 학교 쉬는 시간이 낮잠을 자는데 친구가 갑자기 큰 소리를 내서 잠을 못 잤어.", is_user=True),
                         DialogueTurn("그랬구나. 그때 기분이 어땠어?", is_user=False),
                         DialogueTurn("그냥 기분이 안 좋았어", is_user=True),
                         DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                         DialogueTurn("갑자기 소리를 내서 놀랐고, 화도 났어", is_user=True),
                         DialogueTurn("그랬구나 갑자기 소리내서 놀랐고 화도 냈구나. 그걸 격분하다 또는 매우 화가 많이 났다고 표현해.", is_user=False),
                         DialogueTurn("격분이 뭐야?", is_user=True),
                     ],
                     json.dumps({
                         "assistant_emphasized": True,
                         "assistant_explained": True,
                         "emotion_category": "negative",
                         "identified_emotion_types": ["격분"],
                         "next_phase": "find"
                     })),
                    ([
                         DialogueTurn("어제 친구들이랑 축구를 했어.", is_user=True),
                         DialogueTurn("축구를 했구나! 기분이 어땠어?", is_user=False),
                         DialogueTurn("오랜만에 하는거라 기분이 좋았어", is_user=True),
                         DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                         DialogueTurn("뭔가 기대 됐고 기뻤어", is_user=True),
                         DialogueTurn("오랜만에 친구들이랑 축구를 해서 기대가 되고 기뻤구나. 그걸 낙관적이라고 표현해.", is_user=False),
                         DialogueTurn("낙관이 뭐야?", is_user=True),
                     ],
                     json.dumps({
                         "assistant_emphasized": True,
                         "assistant_explained": True,
                         "emotion_category": "positive",
                         "identified_emotion_types": ["낙관"],
                         "next_phase": "record"
                     })),
                ],

                ###                    [Example]
                ###                    <Child> 어제 학교 쉬는 시간이 낮잠을 자는데 친구가 갑자기 큰 소리를 내서 잠을 못 잤어.
                ###                    <Chatbot> 그랬구나. 그때 기분이 어땠어?
                ###                    <Child> 그냥 기분이 안 좋았어
                #                    <Chatbot> 어떤 기분이 들었는지 자세히 말해줄 수 있을까?
                #                    <Child> 갑자기 소리를 내서 놀랐고, 화도 났어
                #                    <Chatbot>
                #                    <Child>  격분이 뭐야?
                #                    System: "Find" since the Chatbot empathized and explained the user's negative emotions and the key episode (a friend made a big noise while sleeping) and user's negative emotion (격분) is identified.

                #                    <Child> 어제 친구들이랑 축구를 했어.
                #                    <Chatbot> 축구를 했구나! 기분이 어땠어?
                #                    <Child> 오랜만에 하는거라 기분이 좋았어
                #                    <Chatbot> 어떤 기분이 들었는지 자세히 말해줄 수 있을까?
                #                    <Child> 뭔가 기대 됐고 기뻤어
                #                    <Chatbot> 오랜만에 친구들이랑 축구를 해서 기대가 되고 기뻤구나. 그걸 낙관적이라고 표현해.
                #                    <Child>  낙관이 뭐야?
                #                    System: "Record" since the Chatbot empathized and explained the user's positive emotions and the key episode (playing soccer with friends) and user's positive emotion (낙관) is identified.
                gpt_params=ChatGPTParams(temperature=0.5)
            )