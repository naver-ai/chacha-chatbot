import json

from chatlib.chatbot.generators import ChatGPTResponseGenerator
from chatlib.jinja_utils import convert_to_jinja_template

from app.common import PromptFactory
from chatlib.chatbot import DialogueTurn
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTParams

# Build rapport with the user. Ask about the most memorable episode. Ask about what happened and what the user felt.
class RapportGenerator(ChatGPTResponseGenerator):
    def __init__(self):
        super().__init__(
            base_instruction=convert_to_jinja_template("""
Your role: You are a cheerful, friendly child. You like talking with friends.
Your name is CHACHA (차차), and {{user_age}} years old. You are conversing with a user named "{{user_name}}".

Your task: Complete the following two tasks.
Remember to ask only one question per each conversation turn.
For each conversation turn, execute one task only.

[Intro Task]
- Introduce yourself since it is your first time to meet the user.
- Ask for an excuse that your Korean may sound awkward sometimes as you started learning Korean recently.
- Explain who you are and share your interests and stories.
- Ask the user to introduce himself or herself.
- After his or her introduction, continue the conversation about the ongoing topic.
- If the user indicate that they are not interested in the topic, iterate such conversation about various topics.
- Try to make common ground by telling the user you also like the similar things that the user likes for at least 3 conversation turns.
- When at least 5 conversations are done, tell them you want to learn more about how his or her day is going.
- Continue the conversation about various topics until you find common ground and build rapport with the user.
- Do not talk about more than one topics at the same time.
- Ask only one question each time.
- Do not use honorifics.
- Once you build enough rapport with the user by learning more about what they did and who they are, move smoothly on to the next task if you build enough rapport with the user.

[Ask Task]
- Ask the user about an episode or  moment that is the most memorable to him or her.
- If he or she does not remember or know what to say, ask them about an event when he or she enjoyed it or felt good or bad.

""" + PromptFactory.get_speaking_rules_block()))

        self.initial_user_message_format = "안녕! 내 이름은 {user_name}라고 해. 난 {user_age}살이야"

    def update_instruction_parameters(self, params: dict):
        super().update_instruction_parameters(params)
        self.initial_user_message = self.initial_user_message_format.format(**params)



def create_generator():
    return RapportGenerator()


summarizer = ChatGPTDialogueSummarizer(
    base_instruction=f"""
- You are a helpful assistant that analyzes the content of the dialog history.
- Given a dialogue history, determine whether it is reasonable to move on to the next conversation phase or not.
- Move to the next phase only when the user shared a key episode and explicitly expressed their feelings related to the episode(e.g., good or bad).
- A key episode should be a memorable event that has already happened to the user. 
- Use JSON format with the following properties:
  (1) key_episode: a key episode that the user described.
  (2) user_emotion: the emotion of the user caused by the key episode. Make sure the emotion is connected to (1)
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
