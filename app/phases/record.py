import json

from chatlib.chatbot import DialogueTurn, RegenerateRequestException
from chatlib.chatbot.generators import ChatGPTResponseGenerator, StateBasedResponseGenerator
from chatlib.jinja_utils import convert_to_jinja_template
from chatlib.mapper import ChatGPTDialogueSummarizer, ChatGPTDialogSummarizerParams
from chatlib.openai_utils import ChatGPTModel

from app.common import PromptFactory, SPECIAL_TOKEN_CONFIG


# Encourage the user to record the moments in which they felt positive emotions.
def create_generator():
    return ChatGPTResponseGenerator(
        base_instruction=convert_to_jinja_template(PromptFactory.GENERATOR_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES + """
        
- The goal of the current conversation is to encourage the user to keep diary to record the moments in which they felt positive emotions:
{%- for em in identified_emotions | selectattr("is_positive", "true") %}
  * {{em.emotion}} (em.reason)
{%- endfor %}

- 1. First start with asking the user whether they have been keeping diaries or journals regularly.
- 2. Then encourage the user to keep diary to record the moments in which they felt positive emotions.
- 3. Suggest a diary content by explicitly providing an example essay summarizing the above positive emotions and the reason; 
  {%- if locale == 'kr' %}for the essay, use '~다' style Korean, such as "~했다." rather than "~했어.";{%- endif %} 
  put the diary content wrapped with <diary></diary>, at the end of the message;
  {%- if locale == 'kr' %}use the phrase like "예를 들어 다음과 같은 내용으로 일기를 써볼 수 있을 거야."{%- endif %}
  
- Since the user is currently conversing with you, don't ask them to record now.""" + """
{% if summarizer_result != Undefined -%}

[Guide to the conversation]
{% if summarizer_result.asked_user_keeping_diary is false -%}
- You still did not ask whether the user is keeping diary these days. Ask about it.
{%- elif summarizer_result.explained_importance_of_recording is false %}
- You still did not explain the importance of recording the emotions. Explain it.
{%- elif summarizer_result.reflection_note_content_provided is false %}
- You still did not provide the example diary content. Provide it.
{%- endif %}
{%- endif %}

""" + PromptFactory.get_speaking_rules_block()), special_tokens=SPECIAL_TOKEN_CONFIG
    )


class RecordPhaseDialogSummarizer(ChatGPTDialogueSummarizer):
    def __init__(self):
        super().__init__(base_instruction=convert_to_jinja_template("""
- You are a helpful assistant that analyzes the content of the dialogue history.
""" +
                                                                    PromptFactory.SUMMARIZER_PROMPT_BLOCK_KEY_EPISODE_AND_EMOTION_TYPES + """
- The AI in the dialogue is encouraging the user to record the moments in which they felt positive emotions: {{ identified_emotions | selectattr("is_positive", "true") | map(attribute="emotion") | join(", ") }}.

- Analyze the input dialogue and identify if the AI had sufficient conversation about the recording.
Follow this JSON format: {
    "asked_user_keeping_diary": boolean // true if the AI had asked whether the user is keeping diary at present.
    "explained_importance_of_recording": boolean // true if the AI had described the importance of recording positive moments.
    "reflection_note_content_provided": boolean // Whether the AI has provided the reflection note to the user with <diary> tag.
}.
"""), model=ChatGPTModel.GPT_3_5_16k_latest,
                         dialogue_filter=lambda dialogue, _: StateBasedResponseGenerator.trim_dialogue_recent_n_states(
                             dialogue, 3),
     examples=[
                    ([
                        DialogueTurn("오늘 좋았던 기분을 일기에 써보는건 어때?", is_user=False),
                        DialogueTurn("뭐라고 써야 할지 모르겠어", is_user=True),
                        DialogueTurn("이런식으로 써도 좋을 것 같아! <diary>오늘은 정말 감동적인 하루였다. 친구들과 축구를 했는데, 내가 역전골을 넣어서 정말 신났다.</diary>", is_user=False),
                    ],
                    json.dumps({
                            "asked_user_keeping_diary": False,
                            "explained_importance_of_recording": False,
                            "reflection_note_content_provided": True,
                    })),
                    ([
                        DialogueTurn("응. 오늘 오랜만에 친구들을 만나서 행복했어", is_user=True),
                        DialogueTurn("그랬구나. 윤수는 혹시 일기같은 걸 써?", is_user=False),
                        DialogueTurn("근데 난 일기 같은거 안써", is_user=True),
                        DialogueTurn("오늘 행복했던 기분을 일기에 써보는 건 어때? 일기 쓰는 건 처음에는 좀 어색할 수 있지만, 시간이 지날수록 이런 감정들을 기록하고 되돌아보는 게 재미있단다.", is_user=False)
                    ],
                    json.dumps({
                            "asked_user_keeping_diary": True,
                            "explained_importance_of_recording": True,
                            "reflection_note_content_provided": False,
                    })),
        ]
)

    def _postprocess_chatgpt_output(self, output: str, params: ChatGPTDialogSummarizerParams | None = None) -> dict:
        result = super()._postprocess_chatgpt_output(output, params)
        try:
            result["proceed_to_next_phase"] = result["asked_user_keeping_diary"] == True and result["explained_importance_of_recording"] == True and result["reflection_note_content_provided"] == True
            return result
        except:
            raise RegenerateRequestException("Malformed data.")

summarizer = RecordPhaseDialogSummarizer()
