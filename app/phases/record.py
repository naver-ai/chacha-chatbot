from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.jinja_utils import convert_to_jinja_template
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTModel
from chatlib.chatbot import DialogueTurn

import json
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
"""+
PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES + """
- The assistant in the dialogue is encouraging the user to record the moments in which they felt positive emotions.
- Analyze the input dialogue and identify if the assistant had sufficient conversation about the recording.
Follow this JSON format: {
  "proceed_to_next_phase": boolean // true if it is proper moment to proceed to the next conversation phase
  "emotion_summary": String // One-line summary of each emotion that also includes why the user felt the emotion 
}.
"""),
 examples=[
                ([
                    DialogueTurn("오늘 좋았던 기분을 일기에 써보는건 어때?", is_user=False),
                    DialogueTurn("뭐라고 써야 할지 모르겠어", is_user=True),
                    DialogueTurn("'친구들이랑 축구를 했는데 골을 넣어서 기뻤다'. 이런식으로 써도 좋을 것 같아!", is_user=False),
                ],
                json.dumps({
                        "proceed_to_next_phase": True,
                        "emotion_summary": "The user felt joy sine they scored a goal when they played soccer with their friends today",
                })),
                ([
                    DialogueTurn("응. 오늘 오랜만에 친구들을 만나서 행복했어", is_user=True),
                    DialogueTurn("그랬구나. 오늘 좋았던 기분을 일기에 써보는건 어때?", is_user=False),
                    DialogueTurn("근데 난 일기 같은거 안써", is_user=True),
                ],
                json.dumps({
                        "proceed_to_next_phase": False,
                        "emotion_summary": "The user felt happy sine they met their friends after a while",
                })),
    ],
    model=ChatGPTModel.GPT_3_5_latest,
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, 3)
)
