import json
from os import getcwd, path

from chatlib.chatbot import Dialogue, DialogueTurn, RegenerateRequestException
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.utils.jinja_utils import convert_to_jinja_template
# Help the user label their emotion based on the Wheel of Emotions. Empathize their emotion.
from chatlib.tool.versatile_mapper import DialogueSummarizer, MapperInputOutputPair
from chatlib.llm.integration.openai_api import ChatGPTModel, GPTChatCompletionAPI
from chatlib.tool.converter import generate_pydantic_converter

from app.common import EmotionChatbotSpecialTokens, PromptFactory, SPECIAL_TOKEN_CONFIG
from app.common import LabeledEmotionInfo
from app.common import LabelSummarizerResult
from app.common import LabelDialogueSummarizerParams
from app.common import fix_broken_json

from app.models.HyperClovaXAPI import HyperClovaXResponseGenerator, HyperClovaXAPI

emotion_list = None


def _get_emotion_list() -> list[dict]:
    global emotion_list
    if emotion_list is None:
        with open(path.join(getcwd(), "app/emotions.json")) as f:
            emotion_list = json.load(f)

    return emotion_list


def create_generator():
    return HyperClovaXResponseGenerator(base_instruction=convert_to_jinja_template(f"""
{PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_DESC}
- 사용자에게 해당 감정에 대해, 그리고 그 감정을 느끼게 된 이유에 대해 더 자세히 설명해달라고 요청해.

[감정 라벨링 임무]
- 사용자가 스스로 감정을 설명할 수 있도록 열린 질문부터 시작해.
- 사용자가 감정을 어떻게 설명해야 할지 모르겠다고 명시적으로 말하거나, 감정을 모호하게 표현했을 때만 (예: 기분이 좋다/나쁘다), 감정 목록에서 선택할 수 있다고 말하고, 끝에 특별 토큰 {EmotionChatbotSpecialTokens.EmotionSelect}를 추가해.
"""
                                                                               f"""
    - 특별 토큰과 함께, 사용자는 감정 목록에서 하나 이상의 감정을 선택할 거야: {", ".join([emotion['kr'] for emotion in _get_emotion_list()])}.
"""+"""
    - 감정 단어 목록을 언급하지 마. GUI로 표시될 거야.
    - 화면에 표시된 감정 이름 중에서 한 개 혹은 그 이상을 <em>선택</em>하고, <em>'보내기'</em>를 눌러봐"와 같은 표현을 사용해.
    """
                                                                               """
        - 사용자의 선택은 JSON 목록 형태로 전달될 거야. [{"key": ...}, {"key":"..."}, ...] 형식으로, 'key'에는 감정 이름이 들어있어.
        
{% if summarizer_result != Undefined %}
[대화의 현재 상황]
- 현재 너와 사용자는 {{summarizer_result.identified_emotions | count}}개의 감정을 식별한 것 같아: {{summarizer_result.identified_emotions | map(attribute="emotion") | list | list_with_conjunction}}.
{%- set incomplete_positive_emotions = summarizer_result.identified_emotions | selectattr("is_positive", "true") | selectattr("reason", "none") | list -%}
{%- set negative_emotions = summarizer_result.identified_emotions | selectattr("is_positive", "false") | list -%}
{%- if incomplete_positive_emotions | length > 0 -%} {# If there exist positive emotions with no reasons... #}
- 하지만 긍정적인 감정 {{incomplete_positive_emotions | map(attribute="emotion") | list | list_with_conjunction}}은 더 설명이 필요해. 따라서 사용자에게 {%-if incomplete_positive_emotions | length > 1-%}이 감정들에 대해 하나의 열린 질문으로 설명해달라고 요청해.{%-else-%}그 이유를 설명해달라고 요청해.{%-endif%}
{%- elif negative_emotions | length > 0 -%} {# If no incomplete positive emotions, turn to negative emotions one by one. #}
{%- set emotion_without_reason = summarizer_result.identified_emotions | selectattr("reason", "none") | first | default(None) -%}
{% if emotion_without_reason is not none %} 
  - 하지만 {{emotion_without_reason.emotion}}은 더 설명이 필요해. 따라서 사용자에게 {{emotion_without_reason.emotion}}을 느끼게 된 이유를 설명해달라고 요청해. 
{% else %}
{%- set emotion_without_empathy = summarizer_result.identified_emotions | selectattr("empathized", "false") | first | default(None) -%}
{% if emotion_without_empathy is not none %}
- 하지만 너는 사용자의 {{emotion_without_empathy.emotion}}에 대해 공감하지 않았어. 따라서 사용자의 감정인 "{{emotion_without_empathy.emotion}}"에 대해 더 명시적으로 공감해.{% endif %}
{% endif %}
{%- endif -%}
{%- endif %}

[대화 규칙]
- 사용자가 어떻게 느꼈는지 다시 한 번 짚어주고, 사용자와 비슷한 너의 경험을 공유해서 사용자의 감정에 공감해.
- 사용자가 여러 감정을 언급했었다면, 사용자가 선택한 각 감정에 대해 공감해.
- 사용자가 여러 감정을 언급했었다면, 메시지마다 하나씩 사용자에게 각 감정을 어떻게 느끼는지 물어봐.
- 사용자의 주요 에피소드에 다른 사람들이 관련되어 있다면, 사용자에게 그 사람들이 어떻게 느꼈을지 물어봐.
- 사용자가 표현한 모든 감정이 다뤄질 때까지 대화를 계속해.

""" + PromptFactory.get_speaking_rules_block()),
                                    special_tokens=SPECIAL_TOKEN_CONFIG)

_summarizer_prompt_template = convert_to_jinja_template("""
- 너는 대화 내용을 분석하는 도움이 되는 챗봇 연구 분석가야.
- AI와 사용자 간의 주어진 대화를 분석하고, 사용자의 주요 에피소드 ("{{key_episode}}")와 그에 대한 감정 ("{{user_emotion}}")에 대해 충분한 소통이 있었는지 식별해.
- AI의 목표는 사용자가 자신의 감정과 그 배경 이유를 설명하도록 유도하고, 사용자에게 충분히 공감하는 거야.
- 사용자는 감정을 열린 방식으로 설명할 수 있어. 그렇지 않으면, 사용자는 선택적으로 '[{"key": ...}, {"key": ...}, ...]'와 같은 JSON 형식의 목록을 제공할 수 있어."""f""" 여기서 'key'는 사용자가 목록에서 선택한 감정의 이름을 포함해: {", ".join([em['kr'] for em in _get_emotion_list()])}.
""" + """
- 다음 형식으로 JSON을 반환해:
    {
     "identified_emotions": Array<
        {
            "emotion": string, // 감정의 이름
            "reason": string | null, // 그 감정을 느끼게 된 이유를 요약 (사용자가 아직 이유를 설명하지 않았다면 null)
            "ai_empathy": string | null, // AI가 이 감정에 대해 어떻게 코멘트했는지
            "empathized": boolean, // AI가 이 감정에 대해 명시적으로 코멘트했는지 여부
            "is_positive": boolean // 감정이 긍정적인 것으로 분류될 수 있으면 true, 부정적이면 false
        }
     > 
    }

아래 예시들을 참고해.
""")

def _generate_instruction(dialogue: Dialogue, params: LabelDialogueSummarizerParams)->str:
     return _summarizer_prompt_template.render(key_episode=params.key_episode, user_emotion=params.user_emotion)

_str_to_result, _result_to_str = generate_pydantic_converter(LabelSummarizerResult)

def str_to_result(model_output: str, params: LabelDialogueSummarizerParams) -> LabelSummarizerResult:
    try:
        model_output = fix_broken_json(model_output)
        result = _str_to_result(model_output, params)
        if len(result.identified_emotions) > 0:
            emotion_infos = result.identified_emotions
            if len([em for em in emotion_infos if
                        em.reason is None or (em.empathized is False and em.is_positive is False)]) > 0: # Don't take empathized into account for positive emotions.
                result.next_phase = None
                return result
            else:
                result.next_phase = "find" if len(
                    [em for em in emotion_infos if em.is_positive == False]) > 0 else "record"
                return result
        else:
            result.next_phase = None
            return result
    except:
        raise RegenerateRequestException("Malformed data.")
     

summarizer = DialogueSummarizer(
    api= HyperClovaXAPI(),
    instruction_generator=_generate_instruction,
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(
                             dialogue, 2),
    output_str_converter=_result_to_str,
    str_output_converter=str_to_result
    )


summarizer_examples=[MapperInputOutputPair(
                            input=[
                                DialogueTurn(message="어제 학교 쉬는 시간이 낮잠을 자는데 친구가 갑자기 큰 소리를 내서 잠을 못 잤어.", is_user=True),
                                DialogueTurn(message="그랬구나. 그때 기분이 어땠어?", is_user=False),
                                DialogueTurn(message="그냥 기분이 안 좋았어", is_user=True),
                                DialogueTurn(message="어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                                DialogueTurn(message="놀라고 화도 났어", is_user=True),
                                DialogueTurn(message="그랬구나 놀라고 화가 많이 났구나. 어떤 상황에서 놀랐어?", is_user=False),
                                DialogueTurn(message="내 바로 옆에서 갑자기 큰소리가 나 놀랐어", is_user=True),
                                DialogueTurn(message="그랬구나 그래서 놀랐구나. 그러면 어떤 상황에서 화가 났어?", is_user=False),
                                DialogueTurn(message="그 친구가 사과도 없이 계속 시끄럽게 해서 화가 났어", is_user=True),
                            ],
                            output= LabelSummarizerResult(identified_emotions = [
                                    LabeledEmotionInfo(
                                        emotion="Surprise",
                                        reason="사용자가 바로 옆에서 갑자기 큰 소리를 들었다.",
                                        empathized=True,
                                        ai_empathy="AI가 \"그랬구나 놀라고 화가 많이 났구나\" 또는 \"그랬구나 그래서 놀랐구나\"와 같이 공감했다.",
                                        is_positive=True),
                                    
                                    LabeledEmotionInfo(
                                        emotion="Anger",
                                        reason="친구가 사과도 없이 계속 시끄럽게 해서 사용자가 화가 났다.",
                                        ai_empathy=None,
                                        empathized=False, 
                                        is_positive=False)
                                  ])),
                        MapperInputOutputPair(input=[
                                  DialogueTurn(message="어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                                  DialogueTurn(message="슬프고 후회돼", is_user=True),
                                  DialogueTurn(message="그랬구나 슬프고 후회됐구나. 어떤 상황이 슬펐어?", is_user=False),
                                  DialogueTurn(message="달리기 연습을 많이 했는데 넘어져서 꼴등을 한게 슬퍼", is_user=True),
                                  DialogueTurn(message="그랬구나, 꼴찌를 해서 슬픈 거였구나.", is_user=False),
                              ],
                            output= LabelSummarizerResult(identified_emotions=[
                                      LabeledEmotionInfo(
                                          emotion="Sadness",
                                          reason="사용자가 달리기 연습을 많이 했는데도 넘어져서 꼴등을 해서 슬펐다.",
                                          empathized=True,
                                          ai_empathy="AI가 \"그랬구나, 꼴찌를 해서 슬픈 거였구나\"와 같이 사용자의 슬픔에 공감했다.",
                                          is_positive=False),
                                      LabeledEmotionInfo(emotion="Regret", reason=None, empathized=False, ai_empathy=None,
                                       is_positive=False)]
                            )),
                        MapperInputOutputPair(input=[
                                  DialogueTurn(message="어제 숙제를 다 못 해서 옆에 친구 숙제를 배꼈어.", is_user=True),
                                  DialogueTurn(message="숙제를 못 해서 그랬었구나. 기분이 어땠어?", is_user=False),
                                  DialogueTurn(message="기분이 안 좋았어", is_user=True),
                                  DialogueTurn(message="어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                                  DialogueTurn(message="뭔가 후회돼", is_user=True),
                              ],
                              output=LabelSummarizerResult(identified_emotions=[
                                    LabeledEmotionInfo(
                                        emotion="Regret",
                                        reason="사용자가 친구의 숙제를 베껴서 후회했다.",
                                        empathized=False, 
                                        ai_empathy=None,
                                        is_positive=False)])),
                         ]