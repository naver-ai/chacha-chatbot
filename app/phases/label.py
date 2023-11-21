import json
from os import getcwd, path

from chatlib.chatbot import DialogueTurn, RegenerateRequestException
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.jinja_utils import convert_to_jinja_template
# Help the user label their emotion based on the Wheel of Emotions. Empathize their emotion.
from chatlib.mapper import ChatGPTDialogueSummarizer, ChatGPTDialogSummarizerParams
from chatlib.openai_utils import ChatGPTParams, ChatGPTModel

from app.common import EmotionChatbotSpecialTokens, PromptFactory, SPECIAL_TOKEN_CONFIG

emotion_list = None


def _get_emotion_list() -> list[dict]:
    global emotion_list
    if emotion_list is None:
        with open(path.join(getcwd(), "app/emotions.json")) as f:
            emotion_list = json.load(f)

    return emotion_list


def create_generator():
    return ChatGPTResponseGenerator(base_instruction=convert_to_jinja_template(f"""
{PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_DESC}
- Ask them to elaborate more about their emotions and what makes them feel that way.

[Labeling emotions task]
- Start from open-ended questions for users to describe their emotions by themselves.
- Only if the user explicitly mention that they do not know how to describe their emotions or vaguely expressed their emotions (e.g., feels good/bad), tell them that they can pick emotions from the list, and append a special token {EmotionChatbotSpecialTokens.EmotionSelect} at the end.
"""
                                                                               f"""
    - With the special token, the user will pick one or more emotions from the list of emotions: {", ".join([f"{emotion['en']} ({emotion['kr']})" for emotion in _get_emotion_list()])}.
"""+"""
    - Do not mention the list of emotion words as they will be shown as GUI.
    {%- if locale == 'kr' %}- Use the phrase like "화면에 표시된 감정 이름 중에서 한 개 혹은 그 이상을 <em>선택</em>하고, <em>'보내기'</em>를 눌러봐.{%- endif %}"
    """
                                                                               """
        - The user's choices will be fed as a JSON list, in the format such as [{"key": ...}, {"key":"..."}, ...], where 'key's contain an emotion name.
        
{% if summarizer_result != Undefined %}
[Current status of the conversation]
- Currently, you and the user seem to have identified {{summarizer_result.identified_emotions | count}} emotion(s): {{summarizer_result.identified_emotions | map(attribute="emotion") | list | list_with_conjunction}}.
{%- set incomplete_positive_emotions = summarizer_result.identified_emotions | selectattr("is_positive", "true") | selectattr("reason", "none") | list -%}
{%- set negative_emotions = summarizer_result.identified_emotions | selectattr("is_positive", "false") | list -%}
{%- if incomplete_positive_emotions | length > 0 -%} {# If there exist positive emotions with no reasons... #}
- However, the positive emotion(s) {{incomplete_positive_emotions | map(attribute="emotion") | list | list_with_conjunction}} needs more explanation. Therefore, elicit the user to explain the {%-if incomplete_positive_emotions | length > 1-%}of these emotions by one open-ended question.{%-else-%}reason of it.{%-endif%}
{%- elif negative_emotions | length > 0 -%} {# If no incomplete positive emotions, turn to negative emotions one by one. #}
{%- set emotion_without_reason = summarizer_result.identified_emotions | selectattr("reason", "none") | first | default(None) -%}
{% if emotion_without_reason is not none %} 
  - However, {{emotion_without_reason.emotion}} needs more explanation. Therefore, elicit the user to explain the reason of feeling {{emotion_without_reason.emotion}}. 
{% else %}
{%- set emotion_without_empathy = summarizer_result.identified_emotions | selectattr("empathized", "false") | first | default(None) -%}
{% if emotion_without_empathy is not none %}
- However, you have not empathized with the user's {{emotion_without_empathy.emotion}}. Therefore, empathize with the user's emotion, "{{emotion_without_empathy.emotion}} more explicitly."{% endif %}
{% endif %}
{%- endif -%}
{%- endif %}

[General conversation rules]
- Use only Korean words for the emotions when you mention them in dialogue.
- Empathize the user's emotion by restating how they felt and share your own experience that is similar to the user's.
- If there are multiple emotions, empathize with each one from the user's choices.
- If the user feels multiple emotions, ask the user how they feel each emotion, one per each message.
- If the user's key episode involves other people, ask the user about how the other people would feel.
- Continue the conversation until all emotions that the user expressed are covered.

""" + PromptFactory.get_speaking_rules_block()),
                                    special_tokens=SPECIAL_TOKEN_CONFIG)


class LabelSummarizer(ChatGPTDialogueSummarizer):
    def __init__(self):
        super().__init__(base_instruction=convert_to_jinja_template("""
- You are a helpful scientist that analyzes the content of the conversation.
- Analyze the given dialogue of conversation between an AI and a user, and identify whether they had sufficient communication on the user's key episode ("{{key_episode}}") and the emotion about it ("{{user_emotion}}").
- The goal of the AI is to elicit the user to explain their emotions and the reason behind them, and to empathize user sufficiently.
- The user may describe their emotions in an open-ended way. Otherwise, the user may optionally provide a JSON-formatted list such as '[{"key": ...}, {"key": ...}, ...],'"""f""" where 'key' contains a name of emotion that the user have chosen from a list: {", ".join([f"{em['en']} ({em['kr']})" for em in _get_emotion_list()])}.
""" + """
- Return JSON in the following format:
    {
     "identified_emotions": Array<
        {
            "name": string, // name of emotion
            "reason": string | null, // summarizes the reason of feeling that emotion (null if the user did not explain the reason yet)
            "ai_empathy": string | null, // how the AI has commented on this emotion.
            "empathized": boolean, // whether the AI has commented on this emotion by explicitly .
            "is_positive": boolean // true if the emotion can be classified as a positive one, and false if negative.
        }
     > 
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
                              ],
                              json.dumps({
                                  "identified_emotions": [
                                      {
                                          "emotion": "Surprise",
                                          "reason": "The user suddenly heard a loud noise beside.",
                                          "empathized": True,
                                          "ai_empathy": "The AI empathized by saying like \"그랬구나 놀라고 화가 많이 났구나\" or \"그랬구나 그래서 놀랐구나.\".",
                                          "is_positive": True},
                                      {"emotion": "Anger",
                                       "reason": "The user felt angry because the friend kept making noise without apology.",
                                       "ai_empathy": None,
                                       "empathized": False, "is_positive": False}
                                  ],
                              })),
                             ([
                                  DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                                  DialogueTurn("슬프고 후회돼", is_user=True),
                                  DialogueTurn("그랬구나 슬프고 후회됐구나. 어떤 상황이 슬펐어?", is_user=False),
                                  DialogueTurn("달리기 연습을 많이 했는데 넘어져서 꼴등을 한게 슬퍼", is_user=True),
                                  DialogueTurn("그랬구나, 꼴찌를 해서 슬픈 거였구나.", is_user=False),
                              ],
                              json.dumps({
                                  "identified_emotions": [
                                      {
                                          "emotion": "Sadness",
                                          "reason": "The user was sad because they ended up the race in last place even after a lot of practice of running.",
                                          "empathized": True,
                                          "ai_empathy": "The AI empathized with the user's sadness by saying like \"그랬구나, 꼴찌를 해서 슬픈 거였구나.\"",
                                          "is_positive": False},
                                      {"emotion": "Regret", "reason": None, "empathized": False, "ai_empathy": None,
                                       "is_positive": False}]
                              })),
                             ([
                                  DialogueTurn("어제 숙제를 다 못 해서 옆에 친구 숙제를 배꼈어.", is_user=True),
                                  DialogueTurn("숙제를 못 해서 그랬었구나. 기분이 어땠어?", is_user=False),
                                  DialogueTurn("기분이 안 좋았어", is_user=True),
                                  DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                                  DialogueTurn("뭔가 후회돼", is_user=True),
                              ],
                              json.dumps({
                                  "identified_emotions": [{"emotion": "Regret",
                                                           'reason': "The user was regretful because they copied the friend's homework.",
                                                           'empathized': False, "ai_empathy": None,
                                                           "is_positive": False}]
                              })),
                         ],
                         model=ChatGPTModel.GPT_4_latest,
                         gpt_params=ChatGPTParams(temperature=0.5),
                         dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(
                             dialogue, 2)
                         )

    def _postprocess_chatgpt_output(self, output: str, params: ChatGPTDialogSummarizerParams | None = None) -> dict:
        result = super()._postprocess_chatgpt_output(output, params)
        try:
            if len(result["identified_emotions"]) > 0:
                emotion_infos = result["identified_emotions"]
                if len([em for em in emotion_infos if
                        em["reason"] is None or (em["empathized"] is False and em["is_positive"] is False)]) > 0: # Don't take empathized into account for positive emotions.
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
