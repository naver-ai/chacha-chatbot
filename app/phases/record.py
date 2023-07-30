from chatlib.chatbot.generators import ChatGPTResponseGenerator
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTModel

from app.common import stringify_list, COMMON_SPEAKING_RULES, EmotionChatbotSpecialTokens


# Encourage the user to record the moments in which they felt positive emotions.
def create_generator():
    return ChatGPTResponseGenerator(
        base_instruction=f"""
- In the previous conversation, the user shared his/her episode (<:key_episode:>) and corresponding emotions (<:identified_emotion_types:>).
- Encourage the user to record the moments in which they felt positive emotions.
- Explain why it is important to record such moments.

General Speaking rules:
{stringify_list(COMMON_SPEAKING_RULES, ordered=True)}  
                """,
    )

summarizer = ChatGPTDialogueSummarizer(
    base_instruction="""
- You are a helpful assistant that analyzes the content of the dialogue history.
- The dialogue is between a child user and an assistant regarding the key episode ({key_episode}) and corresponding emotions ({identified_emotion_types}).
- The assistant in the dialogue is encouraging the user to record the moments in which they felt positive emotions.
- Analyze the input dialogue and identify if the assistant had sufficient conversation about the recording.
Follow this JSON format: {{
  "proceed_to_next_phase": boolean // true if it is proper moment to proceed to the next conversation phase
}}.
""",
    model=ChatGPTModel.GPT_3_5_latest
)
