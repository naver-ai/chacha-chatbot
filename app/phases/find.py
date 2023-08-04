from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTParams, ChatGPTModel
from chatlib.jinja_utils import convert_to_jinja_template

from app.common import PromptFactory


# Help the user find solution to the situation in which they felt negative emotions.
def create_generator():
    return ChatGPTResponseGenerator(
        base_instruction=convert_to_jinja_template(f"""
{PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
- Ask the user about potential solutions to the problem of the episode.
- Ask only one question each conversation turn. 
- If the episode involves other people such as friends or parents, ask the user how they would feel. 
- Help the user to find an "actionable" solution. 
- Do not overly suggest a specific solution.
 
{PromptFactory.get_speaking_rules_block()}
""")
    )


summarizer = ChatGPTDialogueSummarizer(
    base_instruction=convert_to_jinja_template(f"""
- You are a helpful assistant that analyzes the content of the conversation.
{PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
- The AI in the conversation is helping the user to come up with solutions to the problem of the episode.
- Determine whether the user successfully came up with solutions so that it is a reasonable moment to move on to the next conversation phase or not."""+"""
- Return a JSON string in the following format:
{
    "problem": string |null // describe the problem of the episode.
    "identified_solutions": string | null // describe the solutions that the user and the AI have discussed. Set null if no solutions appeared yet.
    "is_actionable": boolean // whether the solution is developed to be sufficiently actionable for the user.
    "ai_comment_to_solution": string | null // how the AI commented on the solutions identified, especially when the solution was raised by the user. Set null if the AI had not commented yet.
    "proceed_to_next_phase": boolean // True if the problem was clearly specified && the solution was identified && the solution is developed actionable && the AI have commented on the solutions.
}
"""),
    model=ChatGPTModel.GPT_3_5_latest,
    gpt_params=ChatGPTParams(temperature=0.5),
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, 3)
)
