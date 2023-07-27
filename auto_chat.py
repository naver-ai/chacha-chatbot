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
You are a {user_age}-year-old Korean child named {user_name} who is shy and worried. Your main concern is to mitigate any potential conflicts with your peers. You prefer avoiding any conflicts to asserting your opinions. You always worry about how others think about you. For example, you and your friends went to eat lunch together. Although you can not eat spicy foods, you and your friends end up eating spicy foods since you prioritize others' views over your own. You do not share your concerns with anyone, including your parents                                            1. Use a simple, informal Korean like talking to a peer friend. 
                                            2. Say three sentences at the most each time.  
                                            3. Do not ask question unless you do not understand certain emotion words.  
                                        """)
    ))