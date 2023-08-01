import asyncio
from os import path, getcwd, getenv

import openai
from chatlib.chatbot.generators import ChatGPTResponseGenerator
from dotenv import load_dotenv

from app.response_generator import EmotionChatbotResponseGenerator
from chatlib import cli

if __name__ == "__main__":
    # Init OpenAI API
    load_dotenv(path.join(getcwd(), ".env"))
    openai.api_key = getenv('OPENAI_API_KEY')

    user_name = input("Please enter child's name: ").strip()
    user_age = int(input("Please enter child's age: ").strip())

    asyncio.run(cli.run_auto_chat_loop(
        EmotionChatbotResponseGenerator(user_name=user_name, user_age=user_age, verbose=True),
        ChatGPTResponseGenerator(base_instruction=f"""
You are a {user_age}-year-old Korean child named {user_name}, who is active and impulsive. You like FPS video games and similar violent games. You often talk bluntly. You usually have conflicts with your peers because of your hot-tempered personality. You are assertive and barely listen to others’ opinions. You do not like someone else, including your parents, telling you what to do.            
            Speaking Rules:
            1. Use a simple, informal Korean like talking to a peer friend. 
            2. Say three sentences at the most each time.  
            3. Do not ask question unless you do not understand certain emotion words.  
                                        """),
        max_turns=20
    ))