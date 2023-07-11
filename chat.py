from os import path, getcwd, getenv

import openai
from dotenv import load_dotenv

from app.response_generator import EmotionChatbotResponseGenerator
from core.chatbot import TurnTakingChatSession
from nanoid import generate as generate_id

import asyncio


def _print_system_message(message: str, metadata: dict | None, elapsed: int):
    print(f"AI: {message} ({metadata.__str__() if metadata is not None else None}) - {elapsed} sec")


def _print_user_message(message: str):
    print(f"You: {message}")


async def run_chat_loop():
    session_id = generate_id()

    print(f"Start a chat session (id: {session_id}).")
    user_name = input("Please enter your name: ").strip()
    user_age = input("Please enter your age: ").strip()
    session = TurnTakingChatSession(session_id,
                                    EmotionChatbotResponseGenerator(user_name=user_name,user_age=user_age))

    _print_system_message(*(await session.initialize()))  # Print initial message

    while True:
        user_message = input("You: ")
        system_message, metadata, elapsed = await session.push_user_message(user_message)
        _print_system_message(system_message, metadata, elapsed)


if __name__ == "__main__":
    # Init OpenAI API
    load_dotenv(path.join(getcwd(), ".env"))
    openai.api_key = getenv('OPENAI_API_KEY')

    asyncio.run(run_chat_loop())
