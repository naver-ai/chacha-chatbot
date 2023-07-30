from chatlib.chatbot.generators import ChatGPTResponseGenerator

from app.common import stringify_list, COMMON_SPEAKING_RULES


# Emergency situation: Provide relevant resources to the user
def create_generator():
    return ChatGPTResponseGenerator(
            base_instruction=f"""
- Provide the following hotline number for children's mental support: 000-0000-0000.
- Provide the list of mental health providers for the user.
- Do not ask too many questions.
- Do not suggest other options.
- Do not overly comfort the user.

General Speaking rules:
{stringify_list(COMMON_SPEAKING_RULES, ordered=True)}
                    """
        )