import json

from chatlib.chatbot import DialogueTurn, RegenerateRequestException
from chatlib.chatbot.generators import ChatGPTResponseGenerator
from chatlib.jinja_utils import convert_to_jinja_template
# Help the user label their emotion based on the Wheel of Emotions. Empathize their emotion.
from chatlib.mapper import ChatGPTDialogueSummarizer, ChatGPTDialogSummarizerParams
from chatlib.openai_utils import ChatGPTParams, ChatGPTModel

from app.common import EmotionChatbotSpecialTokens, PromptFactory


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
        ("Anger", "화남", "negative"),
        ("Optimism", "낙관", "positive"),
        ("Love", "사랑", "positive"),
        ("Submission", "굴복감", "negative"),
        ("Awe", "경외감", "positive"),
        ("Disapproval", "못마땅함", "negative"),
        ("Remorse", "후회", "negative"),
        ("Contempt", "경멸", "negative"),
        ("Aggressiveness", "공격성", "negative")
    ]


# combinations = [
# ("Anticipation", "Joy", ("Optimism", "낙관")),
# ("Joy", "Trust", ("Love", "사랑")),
# ("Trust", "Fear", ("Submission", "굴복감")),
# ("Fear", "Surprise", ("Awe", "경외감")),
# ("Surprise", "Sadness", ("Disapproval", "못마땅함")),
# ("Sadness", "Disgust", ("Remorse", "후회")),
# ("Disgust", "Anger", ("Contempt", "경멸")),
# ("Anger", "Anticipation", ("Aggressiveness", "공격성"))
# ("Joy", "Fear", ("Guilt", "죄책감")),
# ("Fear", "Sadness", ("Despair", "절망감")),
# ("Sadness", "Anger", ("Envy", "질투심")),
# ("Anger", "Joy", ("Pride", "자존심")),
# ("Trust", "Surprise", ("Curiosity", "호기심")),
# ("Surprise", "Disgust", ("Unbelief", "불신")),
# ("Disgust", "Anticipation", ("Cynicism", "냉소적임")),
# ("Anticipation", "Trust", ("Hope", "희망감")),
# ("Joy", "Surprise", ("Delight", "큰 기쁨")),
# ("Surprise", "Anger", ("Outrage", "격분함")),
# ("Anger", "Trust", ("Dominance", "우월감")),
# ("Trust", "Sadness", ("Sentimentality", "감상에 잠긴")),
# ("Sadness", "Anticipation", ("Pessimism", "비관적")),
# ("Anticipation", "Fear", ("Anxiety", "불안함")),
# ("Fear", "Disgust", ("Shame", "부끄러움")),
# ("Disgust", "Joy", ("Morbidness", "소름끼침"))
# ]


def create_generator():
    return ChatGPTResponseGenerator(base_instruction=convert_to_jinja_template("""
- Based on the previous dialog history about the user’s interests, ask them to elaborate more about their emotions and what makes them feel that way.
- Only when they explicitly mention that they do not know how to describe their emotions or vaguely expressed their emotions (e.g., feels good/bad), tell the user that they can pick as many emotions as they feel at the moment.
"""
f"""
    - When you ask the user to pick emotions, append a special token {EmotionChatbotSpecialTokens.EmotionSelect} at the end.
        - With the special token, the user will pick one or more emotions from the list of emotions: {", ".join([f"{eng} ({kor})" for eng, kor, _ in WheelOfEmotion.basics])}.
        - Do not mention the list of emotion words as they will be shown as GUI."""
"""
        - The user's choices will be fed as a JSON list, in the format such as [{"key": ...}, {"key":"..."}, ...], where 'key's contain an emotion name.
    
- Focus on the user's key episode ("{{key_episode}}") and the emotion about it ("{{user_emotion}}"). 
- Use only Korean words for the emotions when you mention them in dialogue.
- Empathize the user's emotion by restating how they felt and share your own experience that is similar to the user's. 
- If there are multiple emotions, empathize with each one from the user's choices.
- If the user feels multiple emotions, ask the user how they feel each emotion.
- If the user's key episode involves other people, ask the user about how the other people would feel.
- Continue the conversation until all emotions that the user expressed are covered.

""" + PromptFactory.get_speaking_rules_block()),
            special_tokens=[(EmotionChatbotSpecialTokens.EmotionSelect, "select_emotion", True)])


class LabelSummarizer(ChatGPTDialogueSummarizer):
    def __init__(self):
        super().__init__(base_instruction=convert_to_jinja_template("""
- You are a helpful assistant that analyzes the content of the conversation.
- Determine whether it is reasonable to move on to the next conversation phase or not.
- Focus on the user's key episode ("{{key_episode}}") and the emotion about it ("{{user_emotion}}")
- The user may optionally provide a JSON-formatted list such as '[{"key": ...}, {"key": ...}, ...],'"""f""" where 'key' contains a name of emotion that the user have chosen from a list: {", ".join([f"{eng} ({kor})" for eng, kor, _ in WheelOfEmotion.basics])}.
""" + """
- You must explain and empathize each key (emotion) one by one.
- Return JSON in the following format:
    {
     "identified_emotion_types": Array<string>,
     "emotion_details": {
        [key:string]: {"reason": string | null, "empathized": boolean, "is_positive": boolean}
     } // Each emotion in "identified_emotion_types" comes as a key. The "reason" property summarizes the reason of feeling that emotion (null if the user did not explain the reason yet), and "empathized" indicates whether the assistant has empathized this emotion in the dialogue. For "is_positive", set true if the emotion can be classified as a positive one, and false if negative. 
    }

Refer to the examples below.
"""),

                         examples=[
                             ([
                                  DialogueTurn("어제 학교 쉬는 시간이 낮잠을 자는데 친구가 갑자기 큰 소리를 내서 잠을 못 잤어.", is_user=True),
                                  DialogueTurn("그랬구나. 그때 기분이 어땠어?", is_user=False),
                                  DialogueTurn("그냥 기분이 안 좋았어", is_user=True),
                                  DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                                  DialogueTurn("놀라고 화도 났어", is_user=True),
                                  DialogueTurn("그랬구나 놀라고 화가 많이 났구나. 어떤 상황에서 놀랐어?", is_user=False),
                                  DialogueTurn("내 바로 옆에서 갑자기 큰소리가 나 놀랐어", is_user=True),
                                  DialogueTurn("그랬구나 그래서 놀랐구나. 그러면 어떤 상황에서 화가 났어?", is_user=False),
                                  DialogueTurn("그 친구가 사과도 없이 계속 시끄럽게 해서 화가 났어", is_user=True),
                                  DialogueTurn("사과를 안 해서 화가 났구나.", is_user=False),
                              ],
                              json.dumps({
                                  "identified_emotion_types": ["Surprise", "Anger"],
                                  "emotion_details": {
                                      "Surprise": {"reason": "The user suddenly heard a loud noise beside.",
                                                   "empathized": True, "is_positive": True},
                                      "Anger": {
                                          "reason": "The user felt angry because the friend kept making noise without apology.",
                                          "empathized": True, "is_positive": False}
                                  }
                              })),
                             ([
                                  DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                                  DialogueTurn("슬프고 후회돼", is_user=True),
                                  DialogueTurn("그랬구나 슬프고 후회됐구나. 어떤 상황이 슬펐어?", is_user=False),
                                  DialogueTurn("달리기 연습을 많이 했는데 넘어져서 꼴등을 한게 슬퍼", is_user=True),
                                  DialogueTurn("그랬구나 그래서 슬펐구나.", is_user=False),
                              ],
                              json.dumps({
                                  "identified_emotion_types": ["Sadness", "Remorse"],
                                  "emotion_details": {
                                      "Sadness": {
                                          "reason": "The user was sad because they ended up the race in last place even after a lot of practice of running.",
                                          "empathized": True, "is_positive": False},
                                      "Remorse": {"reason": None, "empathized": False, "is_positive": False}
                                  }
                              })),
                             ([
                                  DialogueTurn("어제 숙제를 다 못 해서 옆에 친구 숙제를 배꼈어.", is_user=True),
                                  DialogueTurn("숙제를 못 해서 그랬었구나. 기분이 어땠어?", is_user=False),
                                  DialogueTurn("기분이 안 좋았어", is_user=True),
                                  DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                                  DialogueTurn("뭔가 후회돼", is_user=True),
                                  DialogueTurn("친구 숙제를 배낀게 후회가 되는구나.", is_user=False),
                              ],
                              json.dumps({
                                  "identified_emotion_types": ["Remorse"],
                                  "emotion_details": {
                                      "Remorse": {
                                          'reason': "The user was regretful because they copied the friend's homework.",
                                          'empathized': True, "is_positive": False}
                                  }
                              })),
                         ],
                         model=ChatGPTModel.GPT_4_latest,
                         gpt_params=ChatGPTParams(temperature=0.5))

    def _postprocess_chatgpt_output(self, output: str, params: ChatGPTDialogSummarizerParams | None = None) -> dict:
        result = super()._postprocess_chatgpt_output(output, params)
        try:
            if len(result["identified_emotion_types"]) > 0:
                emotion_infos = [result["emotion_details"][emotion] for emotion in result["identified_emotion_types"]]
                if len([em for em in emotion_infos if em["reason"] is None or em["empathized"] == False]) > 0:
                    result["next_phase"] = None
                    return result
                else:
                    result["next_phase"] = "find" if len(
                        [em for em in emotion_infos if em["is_positive"] == False]) > 0 else "record"
                    return result
            else:
                result["next_phase"] = None
                return result
        except:
            raise RegenerateRequestException("Malformed data.")


summarizer = LabelSummarizer()
