from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTModel

from app.common import stringify_list, COMMON_SPEAKING_RULES, EmotionChatbotSpecialTokens, SPECIAL_TOKEN_CONFIG


# Emergency situation: Provide relevant resources to the user
def create_generator():
    return ChatGPTResponseGenerator(
            base_instruction=f"""
- Provide the list of mental health providers for the user.
- Do not ask too many questions.
- Do not suggest too many options.
- Do not overly comfort the user.

General Speaking rules:
{stringify_list(COMMON_SPEAKING_RULES, ordered=True)}
                    """, special_tokens=SPECIAL_TOKEN_CONFIG
        )

summarizer = ChatGPTDialogueSummarizer(
    base_instruction="""
- You are a helpful assistant that analyzes the content of the dialogue history.
- Analyze the input dialogue and identify if the assistant had sufficient conversation about the sensitive topics.
Follow this JSON format: 
{
  "sensitive_topic": boolean // true if the user expressed indication of self-harm, suicide, or death
}
""",
    model=ChatGPTModel.GPT_3_5_latest,
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, 1)
)
