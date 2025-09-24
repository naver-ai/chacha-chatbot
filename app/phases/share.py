from chatlib.utils import dict_utils
from chatlib.chatbot import Dialogue, DialogueTurn, dialogue_utils
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.utils.jinja_utils import convert_to_jinja_template
from chatlib.tool.versatile_mapper import DialogueSummarizer
from chatlib.llm.integration.openai_api import ChatGPTModel, GPTChatCompletionAPI
from chatlib.tool.converter import generate_pydantic_converter
from app.models.HyperClovaXAPI import HyperClovaXResponseGenerator, HyperClovaXAPI

from app.common import EmotionChatbotSpecialTokens, FindDialogueSummarizerParams, PromptFactory, \
    SPECIAL_TOKEN_CONFIG, ShareSummarizerResult


# Encourage the user to share their emotion and the episode with their parents. Ask if they want to talk about other episodes.
def create_generator():
    return HyperClovaXResponseGenerator(
        base_instruction=convert_to_jinja_template(f"""
{PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
- 사용자가 지금까지 이야기했던 감정이나 에피소드를 부모님께 말씀드린 적이 있는지 물어봐.
- 공유하지 않았다면, 부모님과 감정이나 에피소드에 대해 나누는 것이 왜 중요한지 설명하고 공유하도록 격려해.
- 공유했다면 칭찬하고 공유한 후에 무슨 일이 일어났는지 물어봐."""+"""
- 주요 에피소드 ({{key_episode}})에 대한 대화 후에,"""+f"""사용자에게 다른 에피소드를 공유하고 싶은지 물어보고, 질문 끝에 특별 토큰 {EmotionChatbotSpecialTokens.NewEpisode}를 넣어.
- 사용자가 공유할 것이 없거나 인사한다면, 사용자에게 인사하고 메시지 끝에 특별 토큰 {EmotionChatbotSpecialTokens.Terminate}를 추가해."""
"""
        
"""
+ PromptFactory.get_speaking_rules_block()),
        special_tokens=SPECIAL_TOKEN_CONFIG
    )

_summarizer_instruction_template = convert_to_jinja_template(f"""
너는 대화 기록의 내용을 분석하는 도움이 되는 챗봇 연구 분석가야.
{PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
특별 토큰 {EmotionChatbotSpecialTokens.NewEpisode}로 표시된 메시지에서, AI는 사용자에게 새로운 주요 에피소드를 공유하고 싶은지 물어봤어.
주어진 대화를 분석하고 사용자가 새로운 에피소드를 공유하고 싶어하는지 반환해."""
"""
다음 JSON 형식을 따라:
{  
  "share_new_episode": boolean | null // 사용자가 공유하고 싶다는 의사를 표현했다면 true, 사용자가 원하지 않는다면 false, 사용자가 아직 어떤 의도도 표현하지 않았다면 null.
}.
""")

def _generate_instruction(dialogue: Dialogue, params: FindDialogueSummarizerParams)->str:
     return _summarizer_instruction_template.render(key_episode=params.key_episode, identified_emotions=params.identified_emotions)

_str_to_result, _result_to_str = generate_pydantic_converter(ShareSummarizerResult)

summarizer = DialogueSummarizer[ShareSummarizerResult, FindDialogueSummarizerParams](
    api=HyperClovaXAPI(),
    instruction_generator=_generate_instruction,
    output_str_converter=_result_to_str,
    str_output_converter=_str_to_result,
    dialogue_filter=lambda dialogue, params: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, N=1)
)