from chatlib.utils import dict_utils
from chatlib.chatbot import Dialogue, DialogueTurn, dialogue_utils
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.utils.jinja_utils import convert_to_jinja_template
from chatlib.tool.versatile_mapper import DialogueSummarizer
from chatlib.llm.integration.openai_api import ChatGPTModel, GPTChatCompletionAPI
from chatlib.tool.converter import generate_pydantic_converter

from app.common import EmotionChatbotSpecialTokens, FindDialogueSummarizerParams, PromptFactory, \
    SPECIAL_TOKEN_CONFIG, ShareSummarizerResult


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

_summarizer_instruction_template = convert_to_jinja_template(f"""
You are a helpful assistant that analyzes the content of the dialogue history.
{PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
In an a message marked with a special token {EmotionChatbotSpecialTokens.NewEpisode}, the AI asked the user if he or she wants to share a new key episode.
Analyze a given dialogue and return whether the user wants to share a new episode."""
"""
Follow this JSON format:
{  
  "share_new_episode": boolean | null // true if the user expressed a desire to share, false if the user doesn't want to, and null if the user did not express any intention yet.
}.
""")

def _generate_instruction(dialogue: Dialogue, params: FindDialogueSummarizerParams)->str:
     return _summarizer_instruction_template.render(key_episode=params.key_episode, identified_emotions=params.identified_emotions)

_str_to_result, _result_to_str = generate_pydantic_converter(ShareSummarizerResult)

summarizer = DialogueSummarizer[ShareSummarizerResult, FindDialogueSummarizerParams](
    api=GPTChatCompletionAPI(),
    instruction_generator=_generate_instruction,
    output_str_converter=_result_to_str,
    str_output_converter=_str_to_result,
    dialogue_filter=lambda dialogue, params: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, N=1)
)