from chatlib.chatbot.generators import ChatGPTResponseGenerator
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTParams, ChatGPTModel

from app.common import stringify_list, COMMON_SPEAKING_RULES, PromptFactory


# Help the user find solution to the situation in which they felt negative emotions.
def create_generator():
    return ChatGPTResponseGenerator(
            base_instruction=ChatGPTResponseGenerator.convert_to_jinja_template("""
- In the previous conversation, the user shared his/her episode ({{key_episode}}) and corresponding emotions ({{identified_emotion_types}}).
- Ask the user about potential solutions to the problem of the episode.
- If the episode involves other people such as friends or parents, ask the user how they would feel. 
- Help the user to find an actionable solution. 
- Do not overly suggest a specific solution. 
""" + PromptFactory.get_speaking_rules_block())
   )

summarizer = ChatGPTDialogueSummarizer(
                base_instruction="""
- You are a helpful assistant that analyzes the content of the conversation.
- In the conversation, the user has shared his/her episode ({{key_episode}}) and corresponding emotions ({{identified_emotion_types}}).
- The assistant in the conversation is helping the user to come up with solutions to the problem of the episode.
- Determine whether the user successfully came up with solutions so that it is a reasonable moment to move on to the next conversation phase or not.
- Return a JSON string in the following format:
{
    "identified_solutions": string, // describe the solutions that the user and the assistant have discussed. 
    "proceed_to_next_phase": boolean, 
}               """,
                model=ChatGPTModel.GPT_3_5_latest,
                gpt_params=ChatGPTParams(temperature=0.5)
            )