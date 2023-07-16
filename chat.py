import asyncio
from os import path, getcwd, getenv

import openai
from dotenv import load_dotenv
from nanoid import generate as generate_id

from app.response_generator import EmotionChatbotResponseGenerator
from core.chatbot import TurnTakingChatSession


def _print_system_message(message: str, metadata: dict | None, processing_time: int):
    print(f"AI: {message} ({metadata.__str__() if metadata is not None else None}) - {processing_time} sec")


def _print_user_message(message: str):
    print(f"You: {message}")


async def run_chat_loop():
    session_id = generate_id()

    print(f"Start a chat session (id: {session_id}).")
    user_name = input("Please enter your name: ").strip()
    user_age = int(input("Please enter your age: ").strip())
    session = TurnTakingChatSession(session_id,
                                    EmotionChatbotResponseGenerator(user_name=user_name,user_age=user_age))

    system_turn = await session.initialize()
    _print_system_message(system_turn.message, system_turn.metadata, system_turn.processing_time)  # Print initial message

    while True:
        user_message = input("You: ")
        system_turn = await session.push_user_message(user_message)
        _print_system_message(system_turn.message, system_turn.metadata, system_turn.processing_time)


if __name__ == "__main__":
    # Init OpenAI API
    load_dotenv(path.join(getcwd(), ".env"))
    openai.api_key = getenv('OPENAI_API_KEY')

    asyncio.run(run_chat_loop())
