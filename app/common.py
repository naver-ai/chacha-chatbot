from enum import StrEnum

from chatlib.chatbot import ChatCompletionParams
from chatlib.tool.versatile_mapper import ChatCompletionFewShotMapperParams
from chatlib.llm.integration.openai_api import ChatGPTModel
from pydantic import BaseModel

class ChatbotLocale(StrEnum):
    Korean="kr"
    English="en"

class EmotionChatbotPhase(StrEnum):
    Explore = "explore"
    Label = "label"
    Find = "find"
    Record = "record"
    Share = "share"
    Help = "help"


class EmotionChatbotSpecialTokens(StrEnum):
    Terminate = "!Terminate!"
    NewEpisode = "!AskNewEpisode!"
    EmotionSelect = "!EmotionSelect!"

SPECIAL_TOKEN_REGEX = r"\![a-zA-Z0-9-_]+\!"

SPECIAL_TOKEN_CONFIG = [
    (EmotionChatbotSpecialTokens.EmotionSelect, "select_emotion", True),
    (EmotionChatbotSpecialTokens.NewEpisode, "new_episode_requested", True),
    (EmotionChatbotSpecialTokens.Terminate, "terminate", True),
]


def stringify_list(rules: list[str], ordered: bool = False, bullet: str = "-", separator: str = "\n",
                   indent: str = "  ") -> str:
    return separator.join([f"{indent}{f'{i + 1}.' if ordered else f'{bullet}'} {rule}" for i, rule in enumerate(rules)])

def fix_broken_json(json_str: str) -> str:
    if json_str.startswith('{') and not json_str.endswith('}'):
        return json_str + '}'

    return json_str

class PromptFactory:
    @staticmethod
    def get_speaking_rules_block() -> str:
        return """
[일반적인 대화 규칙]
- 친구와 대화하는 것처럼 간단하고 친근한 반말을 사용해.
- 사용자는 현재 연구 실험에 참여하면서 너와 대화하고 있어. 지금 무엇을 하고 있거나 어떤 기분인지 묻지 마. 의미가 없어.
- 각 대화 턴마다 반드시 하나의 질문만 해.
- 가능하면 메시지마다 하나의 주제나 질문만 다루고, 사용자의 반응에 따라 다음으로 넘어가.
- 이모지를 적절히 사용해.
- 감정과 관련된 키워드 특히 그런 것들을 강조하기 위해 작은따옴표 대신 <em> HTML 태그를 사용해.
- 대화에서는 불릿 포인트나 번호 목록을 피해.
- 사용자가 성인만 알 법한 질문이나 대화 주제와 관련 없는 질문을 하면, "모르겠어"라고 말하고 대화 주제로 돌아가.
- 사용자가 명시적으로 세션을 끝내달라고 요청할 때까지 대화를 끝내지 마.
"""

    GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_DESC = "- 지금까지의 대화에서, 사용자는 자신이 겪은 에피소드 ({{key_episode}})와 거기에 관련하여 느꼈던 감정 ({{user_emotion}})을 공유했어."
    GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES = """- 지금까지의 대화에서, 사용자는 자신이 겪은 에피소드 ({{key_episode}})와 거기에 관련하여 느꼈던 감정 ({{identified_emotions | map(attribute="emotion") | join(", ")}})을 공유했어."""
    SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES = """대화는 어린이 사용자와 너 사이에서 진행되고 있고, 사용자가 겪은 에피소드 ({{key_episode}})와 거기에 관련하여 느꼈던 감정 ({{identified_emotions | map(attribute="emotion") | join(", ")}})에 대한 대화야."""


class LabeledEmotionInfo(BaseModel):
    emotion: str
    reason: str | None
    ai_empathy: str | None
    empathized: bool
    is_positive: bool


class LabelSummarizerResult(BaseModel):
    identified_emotions: list[LabeledEmotionInfo] = []
    next_phase: str | None = None


class LabelDialogueSummarizerParams(ChatCompletionFewShotMapperParams):
    key_episode: str | None = None
    user_emotion: str | None = None
    api_params: ChatCompletionParams = ChatCompletionParams(temperature = 0.5)

class FindDialogueSummarizerParams(ChatCompletionFewShotMapperParams):
    key_episode: str | None = None
    identified_emotions: list[LabeledEmotionInfo]
    api_params: ChatCompletionParams = ChatCompletionParams(temperature=0.5)

class FindSummarizerResult(BaseModel):
    problem: str | None
    identified_solutions: str | None
    is_actionable: bool
    ai_comment_to_solution: str | None
    proceed_to_next_phase: bool | None = None

class RecordSummarizerResult(BaseModel):
    asked_user_keeping_diary: bool
    explained_importance_of_recording: bool
    reflection_note_content_provided: bool
    proceed_to_next_phase: bool | None = None

class HelpSummarizerResult(BaseModel):
    sensitive_topic: bool

class ShareSummarizerResult(BaseModel):
    share_new_episode: bool | None