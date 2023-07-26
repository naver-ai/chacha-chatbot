from chatlib.chatbot.generators import ChatGPTResponseGenerator

from app.common import stringify_list, COMMON_SPEAKING_RULES


# Help the user find solution to the situation in which they felt negative emotions.
def create_generator():
    return ChatGPTResponseGenerator(
            base_instruction=f"""
Based on the previous conversation history with the user, ask the user about potential solutions to the problem.
If the episode involves other people such as friends or parents, ask the user how they would feel. 
Help the user to find an actionable solution. 
Do not overly suggest a specific solution. 

General Speaking rules: 
{stringify_list(COMMON_SPEAKING_RULES, ordered=True)}
                    """
   )

