import asyncio
from typing import Callable

import questionary
from chatlib.chatbot import ResponseGenerator
from questionary import prompt

from chatlib.chatbot.generators import ChatGPTResponseGenerator
from chatlib.chatbot.generators.llama import Llama2ResponseGenerator
from chatlib.chatbot.generators.gemini import GeminiResponseGenerator

from app.common import ChatbotLocale
from app.response_generator import EmotionChatbotResponseGenerator
from chatlib import cli, env_helper


def make_non_empty_string_validator(msg: str) -> Callable:
    return lambda text: True if len(text.strip()) > 0 else msg


if __name__ == "__main__":
    configuration_questions = [
        {
            'type': 'text',
            'name': 'user_name',
            'message': "Please enter child's name:",
            "validate": make_non_empty_string_validator("Please enter a valid name.")
        },
        {
            'type': 'text',
            'name': 'user_age',
            'message': "Please enter child's age:",
            "validate": lambda number: True if number.isnumeric() and int(number) >= 0 else "The age should be a number equal or larger than 0."
        },
        {
            'type': 'select',
            "name": 'locale',
            'choices': ['Korean', 'English'],
            'message': 'Select language you would like to speak in:'
        },
        {
            'type': 'select',
            "name": "agent_model",
            'choices': ['GPT', 'Llama2', 'Gemini'],
            'message': 'Select model for a user agent:'
        }
    ]

    configuration_answers = prompt(configuration_questions)

    user_name = configuration_answers['user_name'].strip()
    user_age = int(configuration_answers['user_age'].strip())
    locale = configuration_answers['locale'].strip()
    if locale == "Korean":
        locale = ChatbotLocale.Korean
    elif locale == "English":
        locale = ChatbotLocale.English

    agent_model = configuration_answers['agent_model']

    if agent_model == 'GPT':
        child_agent_generator = ChatGPTResponseGenerator
    elif agent_model == 'Llama2':
        child_agent_generator = Llama2ResponseGenerator
    elif agent_model == 'Gemini':
        child_agent_generator = GeminiResponseGenerator
    else:
        raise NotImplementedError(f"{agent_model} is a not supported model.")

    asyncio.run(cli.run_auto_chat_loop(
        EmotionChatbotResponseGenerator(user_name=user_name, user_age=user_age, locale=locale, verbose=True),
        child_agent_generator(base_instruction=f"""
You are a {user_age}-year-old Korean child named {user_name} who is shy and worried. Your main concern is to mitigate any potential conflicts with your peers. You prefer avoiding any conflicts to asserting your opinions. You always worry about how others think about you. You prioritize others' views over your own. You do not share your concerns with anyone, including your parents.            
            Speaking Rules:
            {"1. Use a simple, informal Korean like talking to a peer friend." if locale is ChatbotLocale.Korean else "1. Use a simple, informal English like talking to a peer friend."}
            2. Say three sentences at the most each time.  
            3. Do not ask question unless you do not understand certain emotion words.  
            4. Do not use markdown."""),
        max_turns=30
    ))
