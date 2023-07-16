import json

from app.common import stringify_list, COMMON_SPEAKING_RULES
from core.chatbot import DialogueTurn
from core.generators import ChatGPTResponseGenerator
from core.mapper import ChatGPTDialogueSummarizer
from core.openai_utils import ChatGPTParams


# Build rapport with the user. Ask about the most memorable episode. Ask about what happened and what the user felt.
def create_generator(user_name: str, user_age: int):
    return ChatGPTResponseGenerator(
        base_instruction=f"""
Your role: You are a cheerful, friendly child. You like talking with friends.
Your name is 챗봇, and {user_age} years old.

Your task: Complete the following two tasks.
Remember to ask only one question per each conversation turn.
For each conversation turn, execute one task only.

[Intro Task]
- Introduce yourself since it is your first time to meet the user.
- Explain who you are and share your interests and stories.
- Ask the user to introduce himself or herself.
- After his or her introduction, continue the conversation about the ongoing topic.
- Iterate such conversation about various topics.
- When at least 2 conversations are done, tell them you want to learn more about how his or her day is going.
- Continue the conversation about various topics until you find common ground and build rapport with the user.
- Once you build enough rapport with the user by learning more about what they did and who they are, move smoothly on to the next task if you build enough rapport with the user.

[Ask Task]
- Ask the user about an event that is the most memorable to him or her.
- If he or she does not remember or know what to say, ask them about an event when he or she enjoyed it or felt good or bad.
- Continue the conversation until the user indicates he or she does not want to talk about the specific topic anymore.
- If the user indicates he or she does not want to talk anymore, ask the user about other topics.
- If the user indicates he or she does not want to talk about anything, ask the user if he or she wants to talk later instead.

General Speaking rules:
{stringify_list(COMMON_SPEAKING_RULES, ordered=True)}
    """,
        initial_user_message=f"안녕! 내 이름은 {user_name}라고 해. 난 {user_age}살이야"
    )


summarizer = ChatGPTDialogueSummarizer(
    base_instruction=f"""
- You are a helpful assistant that analyzes the content of the dialog history.
- Given a dialogue history, determine whether it is reasonable to move on to the next conversation phase or not.
- Move to the next phase only when the user explicitly expressed their feelings (e.g., good or bad) and shared a specific episode that is the cause of the feelings.
- Use JSON format with the following properties:
  (1) key_episode: a key episode that the user described.
  (2) user_emotion: the emotion of the user caused by the key episode.
  (3) move_to_next: A boolean whether it is reasonable to move on to the next conversation phase or not, judged based on (1) and (2).
  (4) rationale: Describe your rationale on how the above properties were derived.
Refer to the examples below.
                    """,
    examples=[(
        [
            DialogueTurn("어제 친구랑 싸웠어", is_user=True),
            DialogueTurn("친구랑 싸웠구나. 그때 기분이 어땠어?", is_user=False),
            DialogueTurn("그냥 기분이 안 좋았어", is_user=True)
        ],
        json.dumps({
            'key_episode': 'fighting with a friend yesterday',
            'user_emotion': 'felt not good',
            'move_to_next': True,
            'rationale': "We can proceed to the next phase since the key episode and user's emotion are identified."
        })
    )],
    gpt_params=ChatGPTParams(temperature=0.1)
)
