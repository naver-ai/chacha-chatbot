from app.common import stringify_list, COMMON_SPEAKING_RULES
from core.generators import ChatGPTResponseGenerator

# Encourage the user to record the moments in which they felt positive emotions.
def create_generator():
    return ChatGPTResponseGenerator(
            base_instruction=f"""
                    Based on the previous conversation history about the user’s interests, encourage the user to record the moments in which they felt positive emotions. 
                    Explain why it is important to record such moments.

                    Speaking rules: 
                    {stringify_list(COMMON_SPEAKING_RULES, ordered=True)}  
                """
        )