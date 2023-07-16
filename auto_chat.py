import asyncio
from os import path, getcwd, getenv

import openai
from dotenv import load_dotenv
from nanoid import generate as generate_id

from app.response_generator import EmotionChatbotResponseGenerator
from core.chatbot import MultiAgentChatSession, DialogueTurn, session_writer
from core.generators import ChatGPTResponseGenerator


def _turn_to_str(turn: DialogueTurn) -> str:
    return f"{'<Child>  ' if turn.is_user else '<Chatbot>'} {turn.message} ({turn.metadata.__str__() if turn.metadata is not None else None}) - {turn.processing_time} sec"


def _on_chat_message(turn: DialogueTurn):
    print(_turn_to_str(turn))


async def run_chat_loop():
    session_id = generate_id()

    print(f"Start a chat session (id: {session_id}).")
    user_name = input("Please enter child's name: ").strip()
    user_age = int(input("Please enter child's age: ").strip())
    session = MultiAgentChatSession(session_id,
                                    EmotionChatbotResponseGenerator(user_name=user_name, user_age=user_age, verbose=True),
                                    user_generator=ChatGPTResponseGenerator(base_instruction=f"""
                                        You are a {user_age}-year-old Korean child named {user_name} who is shy and worried. 
                                        Your main concern is to mitigate any potential conflicts with your peers. You prefer avoiding any conflicts to asserting your opinions. You always worry about how others think about you. Yesterday, you and your friends went to eat lunch together. Although you can not eat spicy foods, you and your friends end up eating spicy foods since you prioritize others' views over your own. You do not share your concerns with anyone, including your parents.
                                        
                                        Speaking rule:
                                        1. Use a simple, informal Korean like talking to a peer friend. 
                                        2. Say three sentences at the most each time.  
                                        3. Do not ask question unless you do not understand certain emotion words.  
                                    """)
                                    )

    dialogue = await session.generate_conversation(15, _on_chat_message)

    output_path = path.join(getcwd(), f"auto_chat_{session_id}.txt")
    with open(output_path, "w") as f:
        f.writelines([f"{_turn_to_str(turn)}\n" for i, turn in enumerate(dialogue)])

    print(f"\nSaved conversation at {output_path}")

if __name__ == "__main__":
    # Init OpenAI API
    load_dotenv(path.join(getcwd(), ".env"))
    openai.api_key = getenv('OPENAI_API_KEY')

    asyncio.run(run_chat_loop())
