from os import path, getcwd, getenv

import openai
from dotenv import load_dotenv

from app.response_generator import EmotionChatbotResponseGenerator
from core.chatbot import TurnTakingChatSession, MultiAgentChatSession, DialogTurn
from nanoid import generate as generate_id

import asyncio

from core.generators import ChatGPTResponseGenerator


def _turn_to_str(turn: DialogTurn, metadata: dict | None, elapsed: int) -> str:
    return f"{'<Child>  ' if turn.is_user else '<Chatbot>'} {turn.message} ({metadata.__str__() if metadata is not None else None}) - {elapsed} sec"


def _on_chat_message(turn: DialogTurn, metadata: dict | None, elapsed: int):
    print(_turn_to_str(turn, metadata, elapsed))


async def run_chat_loop():
    session_id = generate_id()

    print(f"Start a chat session (id: {session_id}).")
    user_name = input("Please enter child's name: ").strip()
    user_age = int(input("Please enter child's age: ").strip())
    session = MultiAgentChatSession(session_id,
                                    EmotionChatbotResponseGenerator(user_name=user_name, user_age=user_age),
                                    user_generator=ChatGPTResponseGenerator(base_instruction=f"""
                                    You are currently role-playing with User, who is acting as an AI chatbot that helps children's emotion awareness. 
                                    Suppose you are a {user_age}-year-old Korean child named {user_name}, who is active and impulsive. You are the oldest child in your family, with one younger brother. You often have conflicts with your peers because of your hot-tempered personality. You are assertive and barely listen to others’ opinions. You do not like someone else, including your parents, telling you what to do.""")
                                    )

    dialogue = await session.generate_conversation(15, _on_chat_message)

    output_path = path.join(getcwd(), f"auto_chat_{session_id}.txt")
    with open(output_path, "w") as f:
        f.writelines([f"{_turn_to_str(*turn)}\n" for i, turn in enumerate(dialogue)])

    print(f"\nSaved conversation at {output_path}")

if __name__ == "__main__":
    # Init OpenAI API
    load_dotenv(path.join(getcwd(), ".env"))
    openai.api_key = getenv('OPENAI_API_KEY')

    asyncio.run(run_chat_loop())
