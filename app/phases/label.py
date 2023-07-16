import json

from app.common import stringify_list, COMMON_SPEAKING_RULES
from core.chatbot import DialogueTurn
from core.generators import ChatGPTResponseGenerator

# Help the user label their emotion based on the Wheel of Emotions. Empathize their emotion.
from core.mapper import ChatGPTDialogueSummarizer
from core.openai_utils import ChatGPTParams

# https://en.wikipedia.org/wiki/Emotion_classification#/media/File:Plutchik_Dyads.png
class WheelOfEmotion:
    basics = [
        ("Joy", "기쁨", "positive"),
        ("Trust", "신뢰", "positive"),
        ("Surprise", "놀람", "positive"),
        ("Anticipation", "기대", "positive"),
        ("Fear", "두려움", "negative"),
        ("Sadness", "슬픔", "negative"),
        ("Disgust", "불쾌함", "negative"),
        ("Anger", "화남", "negative")
    ]

    combinations = [
    ("Anticipation", "Joy", ("Optimism", "낙관")),
    ("Joy", "Trust", ("Love", "사랑")),
    ("Trust", "Fear", ("Submission", "굴복감")),
    ("Fear", "Surprise", ("Awe", "경외감")),
    ("Surprise", "Sadness", ("Disapproval", "못마땅함")),
    ("Sadness", "Disgust", ("Remorse", "후회")),
    ("Disgust", "Anger", ("Contempt", "경멸")),
    ("Anger", "Anticipation", ("Aggressiveness", "공격성")),
    ("Joy", "Fear", ("Guilt", "죄책감")),
    ("Fear", "Sadness", ("Despair", "절망감")),
    ("Sadness", "Anger", ("Envy", "질투심")),
    ("Anger", "Joy", ("Pride", "자존심")),
    ("Trust", "Surprise", ("Curiosity", "호기심")),
    ("Surprise", "Disgust", ("Unbelief", "불신")),
    ("Disgust", "Anticipation", ("Cynicism", "냉소적임")),
    ("Anticipation", "Trust", ("Hope", "희망감")),
    ("Joy", "Surprise", ("Delight", "큰 기쁨")),
    ("Surprise", "Anger", ("Outrage", "격분함")),
    ("Anger", "Trust", ("Dominance", "우월감")),
    ("Trust", "Sadness", ("Sentimentality", "감상에 잠긴")),
    ("Sadness", "Anticipation", ("Pessimism", "비관적")),
    ("Anticipation", "Fear", ("Anxiety", "불안함")),
    ("Fear", "Disgust", ("Shame", "부끄러움")),
    ("Disgust", "Joy", ("Morbidness", "소름끼침"))
    ]


def create_generator():

    base_instruction = f"""
- Based on the previous conversation history about the user’s interests, ask the user to elaborate more about their emotions and what makes him or her feel that way by providing them the 8 emotions. 
- Focus on the user's key episode, "<:key_episode:>", and the emotion about it, "<:user_emotion:>". 
- Give positive 4 emotions if they shared positive feelings, and negative 4 emotions if shared negative feelings. 
- Tell the user that they can pick one or two emotions.
- The emotions are based on Plutchik’s Wheel of Emotions: 
    <Positive emotions> {", ".join([f"{emotion} ({kor})" for emotion, kor, valence in WheelOfEmotion.basics if valence == 'positive'])}
    <Negative emotions> {", ".join([f"{emotion} ({kor})" for emotion, kor, valence in WheelOfEmotion.basics if valence == 'negative'])}
- When you ask the user to pick emotions, append a list of markups so that the system can show it as GUI:
    e.g., <emotion-selection-list><emotion key="Joy"/><emotion key="Anticipation"/>...</emotion-selection-list>
- Use only Korean words for the emotions, when you mention them in dialogue, but use English for markups internally.
- Do not directly mention or academically describe Plutchik’s Wheel of Emotions.

- Empathize the user's emotion by restating how they felt.
- If the user picks two emotions, explain about the combination emotions.
{stringify_list([f"{a} + {b} => {res[0]} ({res[1]})" for a,b, res in WheelOfEmotion.combinations], ordered=True, indent="    ")}

General Speaking rules: 
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

    return ChatGPTResponseGenerator(
        base_instruction=base_instruction.replace("<:", "{").replace(":>", "}")
    )


summarizer = ChatGPTDialogueSummarizer(
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
             "identified_emotion_types": ["Surprise", "Anger"],
             "next_phase": "find"
         })),
        ([
             DialogueTurn("어제 친구들이랑 축구를 했어.", is_user=True),
             DialogueTurn("축구를 했구나! 기분이 어땠어?", is_user=False),
             DialogueTurn("오랜만에 하는 거라 기분이 좋았어", is_user=True),
             DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
             DialogueTurn("뭔가 기대 됐고 기뻤어", is_user=True),
             DialogueTurn("오랜만에 친구들이랑 축구를 해서 기대가 되고 기뻤구나. 그걸 낙관적이라고 표현해.", is_user=False),
             DialogueTurn("낙관이 뭐야?", is_user=True),
         ],
         json.dumps({
             "assistant_emphasized": True,
             "assistant_explained": True,
             "emotion_category": "positive",
             "identified_emotion_types": ["Anticipation", "Joy", "Optimism"],
             "next_phase": "record"
         })),
    ],
    gpt_params=ChatGPTParams(temperature=0.5)
)

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
