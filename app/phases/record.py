from chatlib.chatbot.generators import ChatGPTResponseGenerator
from chatlib.jinja_utils import convert_to_jinja_template
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTModel

from app.common import stringify_list, COMMON_SPEAKING_RULES, EmotionChatbotSpecialTokens, PromptFactory


# Encourage the user to record the moments in which they felt positive emotions.
def create_generator():
    return ChatGPTResponseGenerator(
        base_instruction=convert_to_jinja_template(f"""
{PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
- Encourage the user to record the moments in which they felt positive emotions.
- Explain why it is important to record such moments.
- If the user does not know how to record, provide "emotion_summary" from {summarizer}.

{PromptFactory.get_speaking_rules_block()}
"""),
    )

summarizer = ChatGPTDialogueSummarizer(
    base_instruction=convert_to_jinja_template("""
- You are a helpful assistant that analyzes the content of the dialogue history.
- The dialogue is between a child user and an assistant regarding the key episode ({{key_episode}}) and corresponding emotions ({{identified_emotion_types}}).
- The assistant in the dialogue is encouraging the user to record the moments in which they felt positive emotions.
- Analyze the input dialogue and identify if the assistant had sufficient conversation about the recording.
Follow this JSON format: {
  "proceed_to_next_phase": boolean // true if it is proper moment to proceed to the next conversation phase
  "emotion_summary": String // One-line summary of each emotion that also includes why the user felt the emotion 
}.
"""),
    model=ChatGPTModel.GPT_3_5_latest
)
