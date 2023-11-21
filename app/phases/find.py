import json

from chatlib.chatbot import DialogueTurn
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.jinja_utils import convert_to_jinja_template
from chatlib.mapper import ChatGPTDialogueSummarizer
from chatlib.openai_utils import ChatGPTParams, ChatGPTModel

from app.common import PromptFactory, SPECIAL_TOKEN_CONFIG


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
"""), special_tokens=SPECIAL_TOKEN_CONFIG
    )


summarizer = ChatGPTDialogueSummarizer(
    base_instruction=convert_to_jinja_template(f"""
- You are a helpful assistant that analyzes the content of the conversation.
{PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
- The AI in the conversation is helping the user to come up with solutions to the problem of the episode.
- Determine whether the user successfully came up with solutions so that it is a reasonable moment to move on to the next conversation phase or not."""+"""
- Return a JSON string in the following format:
{
    "problem": string |null // Describe the problem of the episode.
    "identified_solutions": string | null // Describe the solutions that the user and the AI have discussed. Set null if no solutions appeared yet.
    "is_actionable": boolean // Whether the solution is developed to be sufficiently actionable for the user.
    "ai_comment_to_solution": string | null // How the AI commented on the solutions identified, especially when the solution was raised by the user. Set null if the AI had not commented yet.
    "proceed_to_next_phase": boolean // True if the problem was clearly specified && the solution was identified && the solution is developed actionable && the AI have commented on the solutions.
}
"""),
    examples=[
                ([
                    DialogueTurn("어떤 상황에서 화가 났어?", is_user=False),
                    DialogueTurn("친구가 사과도 없이 계속 시끄럽게 해서 화가 났어", is_user=True),
                    DialogueTurn("그랬구나 화가 났구나. 그럼 화가 나서 어떻게 했어?", is_user=True),
                    DialogueTurn("그 친구한테 화를 냈어", is_user=True),
                    DialogueTurn("그리고 화가 풀렸어?", is_user=False),
                    DialogueTurn("아니. 딱히 풀린건 같진 않았어", is_user=True),
                    DialogueTurn("친구는 무슨 기분이였을 것 같아?", is_user=False),
                    DialogueTurn("내가 화내서 친구도 기분이 안 좋았을 것 같아", is_user=True),
                    DialogueTurn("그럼 다음엔 어떻게 해서 화를 풀고 싶어?", is_user=False),
                    DialogueTurn("무조건 화내지말고 친구랑 얘기를 먼저 해야겠어", is_user=True),
                    DialogueTurn("좋은 생각 같아! 다음에 친구를 만나면 너가 어떤 기분이였는지 먼저 말을 해보면 좋을 것 같아", is_user=False),
                ],
                json.dumps({
                        "problem": "The user was angry because their friend keeps making noise.",
                        "identified_solutions": "Talk to the friend about the user's feeling", 
                        "is_actionable": True,
                        "ai_comment_to_solution": "The solution is actionable and it is appropriate to proceed to the next phase",
                        "proceed_to_next_phase": True,
                })),
                ([
                    DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                    DialogueTurn("억울했어", is_user=True),
                    DialogueTurn("그랬구나 억울했구나. 어떤 상황이 억울했어", is_user=False),
                    DialogueTurn("잘 못은 동생이 했는데 엄마나 나만 혼내서 억울했어", is_user=True),
                    DialogueTurn("그랬구나, 너만 혼나서 억울했구나. 그럼, 엄마가 어떻게 해주면 좋겠어?", is_user=False),
                    DialogueTurn("엄마가 혼내기전에 내 얘기도 들어줬으면 좋겠어", is_user=True),
                    DialogueTurn("그래 그러면 그렇게 해달라고 엄마한테 얘기보는건 어떨까?", is_user=False),
                    DialogueTurn("근데 엄마 한테 말을 하려고 하면 내가 형이니까 참으라고만 해", is_user=True),

                ],
                json.dumps({
                        "problem": "The mom scolded the user even when the user's brother made the trouble",
                        "identified_solutions": "Talk to the mom to listen to the user", 
                        "is_actionable": True,
                        "ai_comment_to_solution": "The solution is actionable but it is not a good solution as the mother does not listen to the user. So, it is not appropriate to proceed to the next phase.",
                        "proceed_to_next_phase": False,
                })),
                ([
                    DialogueTurn("어제 숙제를 다 못 해서 옆에 친구 숙제를 배꼈어.", is_user=True),
                    DialogueTurn("숙제를 못 해서 그랬었구나. 기분이 어땠어?", is_user=False),
                    DialogueTurn("기분이 안 좋았어", is_user=True),
                    DialogueTurn("어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                    DialogueTurn("뭔가 후회돼", is_user=True),
                    DialogueTurn("그러면 다음에는 어떻게 하면 좋을까?", is_user=False),
                    DialogueTurn("숙제를 미리미리 다 해야겠어", is_user=True),

                ],
                json.dumps({
                        "problem": "The user copied their friend's homework",
                        "identified_solutions": "Complete the homework early", 
                        "is_actionable": True,
                        "ai_comment_to_solution": "The solution is actionable and it is appropirate to proceed to the next phase",
                        "proceed_to_next_phase": True,
                })),
                
    ],
    model=ChatGPTModel.GPT_3_5_16k_latest,
    gpt_params=ChatGPTParams(temperature=0.5),
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, 3)
)
