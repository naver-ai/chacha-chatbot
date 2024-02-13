import argparse
import asyncio
from os import path, getcwd, getenv

import openai
from chatlib.chat_completion_api import make_non_empty_string_validator
from chatlib.chatbot import TurnTakingChatSession
from dotenv import load_dotenv
from questionary import prompt

from app.common import ChatbotLocale
from app.response_generator import EmotionChatbotResponseGenerator
from chatlib import cli
from chatlib.global_config import GlobalConfig

if __name__ == "__main__":

    GlobalConfig.is_cli_mode = True

    parser = argparse.ArgumentParser()

    parser.add_argument('-session', '--session', dest="session", type=str, help='Session ID to restore chat')

    parser.set_defaults(session=None)

    args = parser.parse_args()

    if args.session is not None and len(args.session) > 0:
        # restore existing session...
        session = TurnTakingChatSession(args.session, EmotionChatbotResponseGenerator())
        session.load()
        asyncio.run(cli.run_chat_loop_from_session(session))
    else:

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
                'default': 'Korean',
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
        else:
            raise ValueError("Unsupported locale.")

        asyncio.run(cli.run_chat_loop(EmotionChatbotResponseGenerator(user_name=user_name,
                                                                      user_age=user_age,
                                                                      locale=locale)))
