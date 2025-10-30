import json

from chatlib.chatbot import DialogueTurn, RegenerateRequestException
from chatlib.chatbot.generators import StateBasedResponseGenerator
from chatlib.utils.jinja_utils import convert_to_jinja_template
from chatlib.tool.versatile_mapper import DialogueSummarizer, Dialogue, DialogueTurn, MapperInputOutputPair
from chatlib.tool.converter import generate_pydantic_converter

from app.models.HyperClovaXAPI import HyperClovaXResponseGenerator, HyperClovaXAPI

from app.common import FindDialogueSummarizerParams, PromptFactory, SPECIAL_TOKEN_CONFIG, RecordSummarizerResult


# Encourage the user to record the moments in which they felt positive emotions.
def create_generator():
    return HyperClovaXResponseGenerator(
        base_instruction=convert_to_jinja_template(PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES + """
        
- 현재 대화의 목표는 사용자가 긍정적인 감정을 느꼈던 순간들을 기록하기 위해 일기를 쓰도록 격려하는 거야:
{%- for em in identified_emotions | selectattr("is_positive", "true") %}
  * {{em.emotion}} ({{em.reason}})
{%- endfor %}

- 1. 먼저 사용자가 정기적으로 일기를 쓰고 있는지 물어봐.
- 2. 그 다음 사용자가 긍정적인 감정을 느꼈던 순간들을 기록하기 위해 일기를 쓰도록 격려해.
- 3. 위의 긍정적인 감정들과 그 이유를 요약한 예시 일기 문단 에세이를 명시적으로 제공해서 일기 내용을 제안해;
  메시지 끝에 <diary></diary>로 감싼 일기 내용을 넣어;
- 사용자가 현재 너와 대화하고 있으니까, 지금 기록하라고 요청하지 마.""" + """
{% if summarizer_result != Undefined -%}

[대화 가이드]
{% if summarizer_result.asked_user_keeping_diary is false -%}
- 아직 사용자가 요즘 일기를 쓰고 있는지 물어보지 않았어. 물어봐.
{%- elif summarizer_result.explained_importance_of_recording is false %}
- 아직 감정을 기록하는 것의 중요성을 설명하지 않았어. 설명해.
{%- elif summarizer_result.reflection_note_content_provided is false %}
- 아직 예시 일기 내용을 제공하지 않았어. 제공해.
{%- endif %}
{%- endif %}

""" + PromptFactory.get_speaking_rules_block()), special_tokens=SPECIAL_TOKEN_CONFIG
    )

_summarizer_instruction_template = convert_to_jinja_template("""
- 너는 대화 기록의 내용을 분석하는 도움이 되는 챗봇 연구 분석가야.
""" +
                                                                    PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES + """
- 대화에서 AI는 사용자가 긍정적인 감정을 느꼈던 순간들을 기록하도록 격려하고 있어: {{ identified_emotions | selectattr("is_positive", "true") | map(attribute="emotion") | join(", ") }}.

- 입력된 대화를 분석하고 AI가 기록에 대해 충분한 대화를 했는지 식별해.
다음 JSON 형식을 따라: {
    "asked_user_keeping_diary": boolean // AI가 사용자가 현재 일기를 쓰고 있는지 물어봤다면 true
    "explained_importance_of_recording": boolean // AI가 긍정적인 순간들을 기록하는 것의 중요성을 설명했다면 true
    "reflection_note_content_provided": boolean // AI가 <diary> 태그와 함께 사용자에게 반성 노트를 제공했는지 여부
}.
- 오로지 JSON만 반환하고, 추가적인 말은 하지 말아줘. 
""")

def _instruction_generator(dialogue: Dialogue, params: FindDialogueSummarizerParams)->str:
    return _summarizer_instruction_template.render(key_episode=params.key_episode, identified_emotions=params.identified_emotions)

_str_to_result, _result_to_str = generate_pydantic_converter(RecordSummarizerResult)

def _str_to_result_func(model_output: str, params: FindDialogueSummarizerParams) -> RecordSummarizerResult:
    try:
        result = _str_to_result(model_output, params)
        result.proceed_to_next_phase = result.asked_user_keeping_diary == True and result.explained_importance_of_recording == True and result.reflection_note_content_provided == True
        return result
    except:
        raise RegenerateRequestException("Malformed data.")


summarizer = DialogueSummarizer[RecordSummarizerResult, FindDialogueSummarizerParams](
    api=HyperClovaXAPI(),
    instruction_generator=_instruction_generator,
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(
                             dialogue, 3),
    output_str_converter=_result_to_str,
    str_output_converter=_str_to_result_func
)
     

summarizer_examples=[MapperInputOutputPair(input=[
                        DialogueTurn(message="오늘 좋았던 기분을 일기에 써보는건 어때?", is_user=False),
                        DialogueTurn(message="뭐라고 써야 할지 모르겠어", is_user=True),
                        DialogueTurn(message="이런식으로 써도 좋을 것 같아! <diary>오늘은 정말 감동적인 하루였다. 친구들과 축구를 했는데, 내가 역전골을 넣어서 정말 신났다.</diary>", is_user=False),
                    ], output= RecordSummarizerResult(
                        asked_user_keeping_diary=False,
                        explained_importance_of_recording= False,
                        reflection_note_content_provided= True)),
                    MapperInputOutputPair(input=[
                        DialogueTurn(message="응. 오늘 오랜만에 친구들을 만나서 행복했어", is_user=True),
                        DialogueTurn(message="그랬구나. 윤수는 혹시 일기같은 걸 써?", is_user=False),
                        DialogueTurn(message="근데 난 일기 같은거 안써", is_user=True),
                        DialogueTurn(message="오늘 행복했던 기분을 일기에 써보는 건 어때? 일기 쓰는 건 처음에는 좀 어색할 수 있지만, 시간이 지날수록 이런 감정들을 기록하고 되돌아보는 게 재미있단다.", is_user=False)
                    ], output= RecordSummarizerResult(
                        asked_user_keeping_diary=True,
                        explained_importance_of_recording=True,
                        reflection_note_content_provided=False,
                    ))
        ]