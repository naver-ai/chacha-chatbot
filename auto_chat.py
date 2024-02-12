import asyncio
from os import path, getcwd, getenv

import openai
from chatlib.chat_completion_api import make_non_empty_string_validator
from chatlib.chatbot.generators import ChatGPTResponseGenerator
from dotenv import load_dotenv
from questionary import prompt

from app.common import ChatbotLocale
from app.response_generator import EmotionChatbotResponseGenerator
from chatlib import cli
from chatlib.global_config import GlobalConfig

if __name__ == "__main__":
    # Init OpenAI API
    GlobalConfig.is_cli_mode = True

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
            "validate": lambda number: True if number.isnumeric() and int(
                number) >= 0 else "The age should be a number equal or larger than 0."
        },
        {
            'type': 'select',
            "name": 'locale',
            'choices': ['Korean', 'English'],
            'message': 'Select language you would like to speak in:'
        }
    ]

    configuration_answers = prompt(configuration_questions)

    user_name = configuration_answers['user_name'].strip()
    user_age = int(configuration_answers['user_age'].strip())
    locale_name = configuration_answers['locale'].strip()
    if locale_name == "Korean":
        locale = ChatbotLocale.Korean
    elif locale_name == "English":
        locale = ChatbotLocale.English

    asyncio.run(cli.run_auto_chat_loop(
        EmotionChatbotResponseGenerator(user_name=user_name, user_age=user_age, locale=locale, verbose=True),
        ChatGPTResponseGenerator(base_instruction=f"""
You are a {user_age}-year-old {locale_name} child named {user_name} who is shy and worried. Your main concern is to mitigate any potential conflicts with your peers. You prefer avoiding any conflicts to asserting your opinions. You always worry about how others think about you. You prioritize others' views over your own. You do not share your concerns with anyone, including your parents.            
            Speaking Rules:
            {"1. Use a simple, informal Korean like talking to a peer friend." if locale is ChatbotLocale.Korean else "1. Use a simple, informal English like talking to a peer friend."}
            2. Say three sentences at the most each time.  
            3. Do not ask question unless you do not understand certain emotion words.  
                                        """),
        max_turns=30
    ))