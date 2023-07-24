import asyncio
from os import path, getcwd, getenv

import openai
from dotenv import load_dotenv

from app.response_generator import EmotionChatbotResponseGenerator
from chatlib import cli


if __name__ == "__main__":
    # Init OpenAI API
    load_dotenv(path.join(getcwd(), ".env"))
    openai.api_key = getenv('OPENAI_API_KEY')


    user_name = input("Please enter your name: ").strip()
    user_age = int(input("Please enter your age: ").strip())

    asyncio.run(cli.run_chat_loop(EmotionChatbotResponseGenerator(user_name=user_name,user_age=user_age)))
