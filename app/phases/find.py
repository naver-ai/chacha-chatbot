from app.common import stringify_list, COMMON_SPEAKING_RULES
from core.generators import ChatGPTResponseGenerator

# Help the user find solution to the situation in which they felt negative emotions.
def create_generator():
    return ChatGPTResponseGenerator(
            base_instruction=f"""
Based on the previous conversation history about the user’s interests, ask the user about potential solutions to the problem.
If the episode involves other people, ask the user how they would feel. 
Help the user to find an actionable solution. 

General Speaking rules: 
{stringify_list(COMMON_SPEAKING_RULES, ordered=True)}
                    """
        )