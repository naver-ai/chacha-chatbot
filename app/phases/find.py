
from chatlib.chatbot import DialogueTurn
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.utils.jinja_utils import convert_to_jinja_template
from chatlib.tool.versatile_mapper import DialogueSummarizer, Dialogue, DialogueTurn, MapperInputOutputPair
from chatlib.llm.integration.openai_api import GPTChatCompletionAPI
from chatlib.tool.converter import generate_pydantic_converter
from app.models.HyperClovaXAPI import HyperClovaXResponseGenerator, HyperClovaXAPI

from app.common import FindDialogueSummarizerParams, FindSummarizerResult, PromptFactory, SPECIAL_TOKEN_CONFIG


# Help the user find solution to the situation in which they felt negative emotions.
def create_generator():
    return HyperClovaXResponseGenerator(
        base_instruction=convert_to_jinja_template(f"""
{PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
- 에피소드에 나타난 문제 혹은 곤란한 상황에 대해서, 사용자에게 잠재적인 해결책은 어떤 것들이 있을지 물어봐.
- 각 대화 턴마다 하나의 질문만 해.
- 에피소드에 친구나 부모 같은 다른 사람들이 관련되어 있다면, 사용자에게 그들이 어떻게 느꼈을지 물어봐.
- 사용자가 "실행 가능한" 해결책을 찾도록 도와줘.
- 특정한 해결책을 과도하게 강요하지 마.
 
{PromptFactory.get_speaking_rules_block()}
"""), special_tokens=SPECIAL_TOKEN_CONFIG
    )


_summarizer_prompt_template = convert_to_jinja_template(f"""
- 너는 대화 내용을 분석하는 도움이 되는 챗봇 연구 분석가야.
{PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES}
- 대화에서 AI는 사용자가 묘사한 에피소드에 나타난 문제 혹은 곤란한 상황에 대한 해결책을 찾도록 도와주고 있어.
- 사용자가 성공적으로 해결책을 찾았는지 판단해서 다음 대화 단계로 넘어갈 합리적인 시점인지 결정해."""+"""
- 다음 형식으로 JSON 문자열을 반환해:
{
    "problem": string |null // 에피소드에 나타난 문제 혹은 곤란한 상황을 설명해.
    "identified_solutions": string | null // 사용자와 AI가 논의한 해결책들을 설명해. 아직 해결책이 나타나지 않았다면 null로 설정해.
    "is_actionable": boolean // 해결책이 사용자에게 충분히 실행 가능하도록 발전되었는지 여부.
    "ai_comment_to_solution": string | null // AI가 식별된 해결책들에 대해 어떻게 코멘트했는지, 특히 사용자가 해결책을 제시했을 때. AI가 아직 코멘트하지 않았다면 null로 설정해.
    "proceed_to_next_phase": boolean // 문제가 명확히 지정되었고 && 해결책이 식별되었고 && 해결책이 실행 가능하도록 발전되었고 && AI가 해결책들에 대해 코멘트했다면 true.
}
""")


def _generate_instruction(dialogue: Dialogue, params: FindDialogueSummarizerParams)->str:
     return _summarizer_prompt_template.render(key_episode=params.key_episode, identified_emotions=params.identified_emotions)


_str_to_result, _result_to_str = generate_pydantic_converter(FindSummarizerResult)

summarizer = DialogueSummarizer(
    api=HyperClovaXAPI(),
    instruction_generator=_generate_instruction,
    output_str_converter=_result_to_str,
    str_output_converter=_str_to_result,
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, 3)
)


summarizer_examples=[
                MapperInputOutputPair(input=[
                    DialogueTurn(message="어떤 상황에서 화가 났어?", is_user=False),
                    DialogueTurn(message="친구가 사과도 없이 계속 시끄럽게 해서 화가 났어", is_user=True),
                    DialogueTurn(message="그랬구나 화가 났구나. 그럼 화가 나서 어떻게 했어?", is_user=True),
                    DialogueTurn(message="그 친구한테 화를 냈어", is_user=True),
                    DialogueTurn(message="그리고 화가 풀렸어?", is_user=False),
                    DialogueTurn(message="아니. 딱히 풀린건 같진 않았어", is_user=True),
                    DialogueTurn(message="친구는 무슨 기분이였을 것 같아?", is_user=False),
                    DialogueTurn(message="내가 화내서 친구도 기분이 안 좋았을 것 같아", is_user=True),
                    DialogueTurn(message="그럼 다음엔 어떻게 해서 화를 풀고 싶어?", is_user=False),
                    DialogueTurn(message="무조건 화내지말고 친구랑 얘기를 먼저 해야겠어", is_user=True),
                    DialogueTurn(message="좋은 생각 같아! 다음에 친구를 만나면 너가 어떤 기분이였는지 먼저 말을 해보면 좋을 것 같아", is_user=False),
                ],
                output= FindSummarizerResult(
                    problem="사용자가 친구가 계속 시끄럽게 해서 화가 났다.",
                    identified_solutions="친구에게 사용자의 기분에 대해 이야기하기", 
                    is_actionable=True,
                    ai_comment_to_solution="해결책이 실행 가능하고 다음 단계로 넘어가기에 적절해",
                    proceed_to_next_phase=True,
                )),
                MapperInputOutputPair(input=[
                    DialogueTurn(message="어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                    DialogueTurn(message="억울했어", is_user=True),
                    DialogueTurn(message="그랬구나 억울했구나. 어떤 상황이 억울했어", is_user=False),
                    DialogueTurn(message="잘 못은 동생이 했는데 엄마나 나만 혼내서 억울했어", is_user=True),
                    DialogueTurn(message="그랬구나, 너만 혼나서 억울했구나. 그럼, 엄마가 어떻게 해주면 좋겠어?", is_user=False),
                    DialogueTurn(message="엄마가 혼내기전에 내 얘기도 들어줬으면 좋겠어", is_user=True),
                    DialogueTurn(message="그래 그러면 그렇게 해달라고 엄마한테 얘기보는건 어떨까?", is_user=False),
                    DialogueTurn(message="근데 엄마 한테 말을 하려고 하면 내가 형이니까 참으라고만 해", is_user=True),

                ],
                output=FindSummarizerResult(
                    problem="사용자의 동생이 잘못했는데도 엄마가 사용자만 혼냈다.",
                    identified_solutions="엄마에게 사용자의 말을 들어달라고 이야기하기", 
                    is_actionable=True,
                    ai_comment_to_solution="해결책은 실행 가능하지만 엄마가 사용자의 말을 듣지 않기 때문에 좋은 해결책이 아니야. 따라서 다음 단계로 넘어가기에 적절하지 않아.",
                    proceed_to_next_phase=False,
                )),
                MapperInputOutputPair(input=[
                    DialogueTurn(message="어제 숙제를 다 못 해서 옆에 친구 숙제를 배꼈어.", is_user=True),
                    DialogueTurn(message="숙제를 못 해서 그랬었구나. 기분이 어땠어?", is_user=False),
                    DialogueTurn(message="기분이 안 좋았어", is_user=True),
                    DialogueTurn(message="어떤 기분이 들었는지 자세히 말해줄 수 있을까?", is_user=False),
                    DialogueTurn(message="뭔가 후회돼", is_user=True),
                    DialogueTurn(message="그러면 다음에는 어떻게 하면 좋을까?", is_user=False),
                    DialogueTurn(message="숙제를 미리미리 다 해야겠어", is_user=True),
                ],
                output=FindSummarizerResult(
                    problem="사용자가 친구의 숙제를 베꼈다.",
                    identified_solutions="숙제를 미리미리 완료하기", 
                    is_actionable=True,
                    ai_comment_to_solution="해결책이 실행 가능하고 다음 단계로 넘어가기에 적절해",
                    proceed_to_next_phase=True,
                )),
                
    ]