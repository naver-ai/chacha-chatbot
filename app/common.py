from enum import StrEnum

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