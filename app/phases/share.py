from core.chatbot.generators import ChatGPTResponseGenerator

from app.common import stringify_list, COMMON_SPEAKING_RULES


# Encourage the user to share their emotion and the episode with their parents. Ask if they want to talk about other episodes.
def create_generator():
    return ChatGPTResponseGenerator(
            base_instruction=f"""
Based on the previous conversation history about the user’s interests, ask the user if they have already shared their emotions and the episode with their parents. 
If not, explain why it is important to share with them and encourage sharing.
If yes, praise them and ask what happened after sharing.

General Speaking rules:
{stringify_list(COMMON_SPEAKING_RULES, ordered=True)}
                    """
        )