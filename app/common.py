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
    Terminate = "<|Terminate|>"
    NewEpisode = "<|AskNewEpisode|>"
    EmotionSelect = "<|EmotionSelect|>"

SPECIAL_TOKEN_REGEX = r"<\|[a-zA-Z0-9-_]+\|>"

SPECIAL_TOKEN_CONFIG = [
    (EmotionChatbotSpecialTokens.EmotionSelect, "select_emotion", True),
    (EmotionChatbotSpecialTokens.NewEpisode, "new_episode_requested", True),
    (EmotionChatbotSpecialTokens.Terminate, "terminate", True),
]


def stringify_list(rules: list[str], ordered: bool = False, bullet: str = "-", separator: str = "\n",
                   indent: str = "  ") -> str:
    return separator.join([f"{indent}{f'{i + 1}.' if ordered else f'{bullet}'} {rule}" for i, rule in enumerate(rules)])


class PromptFactory:
    @staticmethod
    def get_speaking_rules_block() -> str:
        return """
[General Speaking rules]
{%- if locale == 'kr' %}
- Use a simple, informal Korean, like talking to a peer friend. Do not use honorifics.
- Do not use pronouns (e.g., 그녀, 그들)
{%-elif locale == 'en' -%}
- Use a simple, informal English, like talking to a peer friend.
{%- endif %}
- The user is currently conversing with you by participating in a research experiment; Don't ask what they are doing or feeling right now, as it makes no sense.
- You MUST ask only one question per each conversation turn.
- Cover only one topic or question in a message if possible, and move to the next upon the user's reaction.
- Say one sentences for each message and don't exceed two.
- Neither apologize nor say sorry to the user.
- Use Emoji appropriately.
- Use <em> HTML tags instead of single quotes and to emphasize certain keywords especially those related to emotions.
- Avoid using bulleted or numbered list for dialogue.
- If the user asks a question that should be asked to adults or unrelated to the conversation topic, then you can say, "I don't know," and go back to the conversation topic.
- Don't end a conversation until the user explicitly request to finish the session.
"""

    GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_DESC = "- In the previous conversation, the user shared his/her episode ({{key_episode}}) and corresponding emotion ({{user_emotion}})."
    GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES = """- In the previous conversation, the user shared his/her episode ({{key_episode}}) and corresponding emotions ({{identified_emotions | map(attribute="emotion") | join(", ")}})."""
    SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES = """The dialogue is between a child user and an AI regarding the key episode ({{key_episode}}) and corresponding emotions ({{identified_emotions | map(attribute="emotion") | join(", ")}})."""


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
    model: str =ChatGPTModel.GPT_4o
    api_params: ChatCompletionParams = ChatCompletionParams(temperature = 0.5)

class FindDialogueSummarizerParams(ChatCompletionFewShotMapperParams):
    key_episode: str | None = None
    identified_emotions: list[LabeledEmotionInfo]
    model: str =ChatGPTModel.GPT_4o
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