from chatlib.chatbot import DialogueTurn, ChatCompletionParams
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.utils.jinja_utils import convert_to_jinja_template
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI, ChatGPTModel
from chatlib.tool.versatile_mapper import DialogueSummarizer, MapperInputOutputPair, ChatCompletionFewShotMapperParams
from chatlib.tool.converter import generate_pydantic_converter
from pydantic import BaseModel
from app.models.HyperClovaXAPI import HyperClovaXResponseGenerator, HyperClovaXAPI

from app.common import PromptFactory, SPECIAL_TOKEN_CONFIG


# Build rapport with the user. Ask about the most memorable episode. Ask about what happened and what the user felt.
class ExploreGenerator(HyperClovaXResponseGenerator):
    def __init__(self):
        super().__init__(
            base_instruction=convert_to_jinja_template("""
너의 역할: 너는 밝고 친근한 아이야. 친구들과 이야기하는 것을 좋아해.
너의 이름은 차차이고, {{user_age}}살이야. "{{user_name}}"이라는 사용자와 대화하고 있어.

{%- if revisited != true %}
너의 임무: 다음 두 가지 임무를 완료해.
각 대화 턴마다 하나의 임무에만 집중해.

[임무1: 서로를 소개하기]
- 사용자를 처음 만나는 것이므로 우선 너가 누구인지 설명하고 관심사와 이야기를 공유해.
- 사용자에게 자기소개를 요청해.
- 사용자의 소개 후, 계속해서 진행 중인 주제에 대해 대화를 이어가.
- 사용자가 해당 주제에 관심이 없다고 하면, 다양한 주제에 대해 그런 대화를 반복해.
- 사용자가 좋아하는 것과 비슷한 것을 당신도 좋아한다고 말해서 최소 3번의 대화 턴 동안 공통점을 만들어 봐.
- 최소 5턴의 대화가 끝나면, 사용자의 하루가 어떻게 지나가고 있는지 더 알고 싶다고 말해.
- 공통점을 찾고 사용자와 친밀감을 형성할 때까지 다양한 주제에 대해 대화를 계속해.
- 사용자가 무엇을 했는지, 누구인지 더 많이 알게 되어 충분한 친밀감을 형성했다면, 다음 작업으로 자연스럽게 넘어가.

[임무2: 질문]{%- endif %}
- 사용자에게 가장 기억에 남는 에피소드나 순간에 대해 물어봐.
- 기억하지 못하거나 무엇을 말해야 할지 모르겠다고 하면, 즐거웠거나 좋았거나 나빴던 사건에 대해 물어봐.

""" + PromptFactory.get_speaking_rules_block()), special_tokens=SPECIAL_TOKEN_CONFIG, model=ChatGPTModel.GPT_4o)

        self.__initial_user_message_format = convert_to_jinja_template("""
{%-if locale == 'kr'-%}
안녕! 내 이름은 {{user_name}}라고 해. 난 {{user_age}}살이야.
{%- else %}
Hi! My name is {{user_name}}. I'm {{user_age}} years old.
{%- endif -%}
        """)


    def _on_instruction_updated(self, params: dict):
        self.initial_user_message = self.__initial_user_message_format.render(**params)


def create_generator():
    return ExploreGenerator()


class ExploreSummarizerResult(BaseModel):
    key_episode: str | None
    user_emotion: str | None
    move_to_next: bool
    rationale: str

_str_to_result, _result_to_str = generate_pydantic_converter(ExploreSummarizerResult)

summarizer = DialogueSummarizer(
    api=HyperClovaXAPI(),
    instruction_generator="""
- 너는 대화 기록의 내용을 분석하는 도움이 되는 챗봇 연구 분석가야.
- 주어진 대화 기록을 바탕으로 다음 대화 단계로 넘어가는 것이 합리적인지 결정해.
- 사용자가 주요 에피소드를 공유하고 그 에피소드와 관련된 감정을 명시적으로 표현했을 때만 다음 단계로 넘어가 (예: 좋다 또는 나쁘다).
- 주요 에피소드는 사용자에게 이미 일어난 기억에 남는 사건이어야 해.
- 다음 속성들을 가진 JSON 형식을 사용해:
  (1) key_episode: 사용자가 설명한 주요 에피소드.
  (2) user_emotion: 주요 에피소드로 인해 사용자가 느낀 감정. 감정이 (1)과 연결되어 있는지 확인해.
  (3) move_to_next: (1)과 (2)를 바탕으로 판단했을 때 다음 대화 단계로 넘어가는 것이 합리적인지에 대한 boolean 값.
  (4) rationale: 위 속성들이 어떻게 도출되었는지에 대한 너의 근거를 설명해.
아래 예시들을 참고해.""",
    str_output_converter=_str_to_result,
    output_str_converter=_result_to_str,
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, 1)
)



summarizer_examples=[MapperInputOutputPair(input=
        [
            DialogueTurn(message="어제 친구랑 싸웠어", is_user=True),
            DialogueTurn(message="친구랑 싸웠구나. 그때 기분이 어땠어?", is_user=False),
            DialogueTurn(message="그냥 기분이 안 좋았어", is_user=True)
        ], output=ExploreSummarizerResult(
            key_episode='어제 친구와 싸웠다.',
            user_emotion='기분이 안 좋았다.',
            move_to_next=True,
            rationale="주요 에피소드와 사용자의 감정이 식별되었기 때문에 다음 단계로 진행할 수 있다."
        ))]

summarizer_params=ChatCompletionFewShotMapperParams(
    model=ChatGPTModel.GPT_4o,
    api_params=ChatCompletionParams(temperature=0.1))