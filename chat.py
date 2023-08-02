import argparse
import asyncio
from os import path, getcwd, getenv

import openai
from chatlib.chatbot import TurnTakingChatSession
from dotenv import load_dotenv

from app.response_generator import EmotionChatbotResponseGenerator
from chatlib import cli

if __name__ == "__main__":
    # Init OpenAI API
    load_dotenv(path.join(getcwd(), ".env"))
    openai.api_key = getenv('OPENAI_API_KEY')

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
        user_name = input("Please enter your name: ").strip()
        user_age = int(input("Please enter your age: ").strip())

        asyncio.run(cli.run_chat_loop(EmotionChatbotResponseGenerator(user_name=user_name,user_age=user_age)))
