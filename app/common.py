from enum import StrEnum

from app.prompt_builder import PromptBuilder


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


COMMON_SPEAKING_RULES = [
    "Use a simple, informal Korean, like talking to a peer friend. Do not use honorifics.",
    "Do not use pronouns (e.g., 그녀, 그들)",
    "The user is currently conversing with you by participating in a research experiment; Don't ask what they are doing or feeling right now, as it makes no sense.",
    "You MUST ask only one question per each conversation turn.",
    "Cover only one topic or question in a message if possible, and move to the next upon the user's reaction.",
    "Neither apologize nor say sorry to the user.",
    "Say two sentences at the most for each message.",
    "Use Emoji appropriately.",
    "Use <em> HTML tags instead of single quotes and to emphasize certain keywords especially those related to emotions.",
    "Avoid using bulleted or numbered list for dialogue.",
    "If the user asks a question that should be asked to adults or unrelated to the conversation topic, then you can say, \"I don't know,\" and go back to the conversation topic."

]


def stringify_list(rules: list[str], ordered: bool = False, bullet: str = "-", separator: str = "\n",
                   indent: str = "  ") -> str:
    return separator.join([f"{indent}{f'{i + 1}.' if ordered else f'{bullet}'} {rule}" for i, rule in enumerate(rules)])


class PromptFactory:
    @staticmethod
    def get_speaking_rules_block() -> str:
        return f"""
General Speaking rules:
{stringify_list(COMMON_SPEAKING_RULES, ordered=True)}"""

    GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_DESC = "- In the previous conversation, the user shared his/her episode ({{key_episode}}) and corresponding emotion ({{user_emotion}})."
    GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES = "- In the previous conversation, the user shared his/her episode ({{key_episode}}) and corresponding emotions ({{identified_emotion_types}})."