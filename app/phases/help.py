from chatlib.utils.jinja_utils import convert_to_jinja_template
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.tool.versatile_mapper import DialogueSummarizer, ChatCompletionParams, ChatCompletionFewShotMapperParams
from chatlib.llm.integration.openai_api import ChatGPTModel, GPTChatCompletionAPI
from chatlib.tool.converter import generate_pydantic_converter

from app.common import HelpSummarizerResult, PromptFactory


# Emergency situation: Provide relevant resources to the user
def create_generator():
    return ChatGPTResponseGenerator(
        base_instruction=convert_to_jinja_template(f"""
- Provide the list of mental health providers for the user.
- Do not ask too many questions.
- Do not suggest too many options.
- Do not overly comfort the user.

{PromptFactory.get_speaking_rules_block()}""")
    )

_str_to_result, _result_to_str = generate_pydantic_converter(HelpSummarizerResult)

summarizer = DialogueSummarizer[HelpSummarizerResult, ChatCompletionFewShotMapperParams](
    api=GPTChatCompletionAPI(),
    instruction_generator="""
- You are a helpful assistant that analyzes the content of the dialogue history.
- Analyze the input dialogue and identify if the assistant had sufficient conversation about the sensitive topics.
Follow this JSON format: 
{
  "sensitive_topic": boolean // true if the user expressed indication of self-harm, suicide, or death
}
""",
    str_output_converter=_str_to_result,
    output_str_converter=_result_to_str,
    dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(dialogue, 1)
)

summarizer_params = ChatCompletionFewShotMapperParams(
    model=ChatGPTModel.GPT_4o,
    api_params = ChatCompletionParams(temperature = 0.5)
)