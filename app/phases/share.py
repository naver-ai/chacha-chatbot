from chatlib import dialogue_utils, dict_utils
from chatlib.chatbot import Dialogue
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.jinja_utils import convert_to_jinja_template
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTModel

from app.common import EmotionChatbotSpecialTokens, PromptFactory, \
    SPECIAL_TOKEN_CONFIG


# Encourage the user to share their emotion and the episode with their parents. Ask if they want to talk about other episodes.
def create_generator():
    return ChatGPTResponseGenerator(
        base_instruction=convert_to_jinja_template(f"""
{PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
- Ask the user if they have already shared their emotions and the episode with their parents. 
- If not, explain why it is important to share with them and encourage sharing.
- If yes, praise them and ask what happened after sharing."""+"""
- After the conversation about the key episode ({{key_episode}}),"""+f"""ask the user if the user would like to share another episode, and put a special token {EmotionChatbotSpecialTokens.NewEpisode} at the end of the question.
- If the user has nothing to share or byes, bye the user and append a special token {EmotionChatbotSpecialTokens.Terminate} at the end of the message."""
"""
        
"""
+ PromptFactory.get_speaking_rules_block()),
        special_tokens=SPECIAL_TOKEN_CONFIG
    )

__classifier = ChatGPTDialogueSummarizer(
    base_instruction=convert_to_jinja_template(f"""
You are a helpful assistant that analyzes the content of the dialogue history.
{PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
In an a message marked with a special token {EmotionChatbotSpecialTokens.NewEpisode}, the AI asked the user if he or she wants to share a new key episode.
Analyze a given dialogue and return whether the user wants to share a new episode."""
"""
Follow this JSON format:
{  
  "share_new_episode": boolean | null // true if the user expressed a desire to share, false if the user doesn't want to, and null if the user did not express any intention yet.
}.
"""),
    model=ChatGPTModel.GPT_3_5_16k_latest,
    dialogue_filter=lambda dialogue, params: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, N=1)
)

async def check_new_episode_requested(dialogue: Dialogue)->bool | None:
    last_turn_with_flag, last_turn_with_flag_index = dialogue_utils.find_last_turn(dialogue, lambda turn: dict_utils.get_nested_value(turn.metadata, "new_episode_requested") == True)
    if last_turn_with_flag_index != -1 and last_turn_with_flag_index < len(dialogue)-1:
        # if the flagged turn exists and is not the last one...
        result = await __classifier.run(dialogue[last_turn_with_flag_index:])
        return result["share_new_episode"]
    else:
        return None