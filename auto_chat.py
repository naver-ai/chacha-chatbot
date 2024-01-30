import asyncio
from os import path, getcwd, getenv

import openai
from chatlib.azure_llama2_utils import AzureLlama2Environment
from chatlib.chatbot.generators import ChatGPTResponseGenerator
from chatlib.chatbot.generators.llama import Llama2ResponseGenerator
from dotenv import load_dotenv

from app.common import ChatbotLocale
from app.response_generator import EmotionChatbotResponseGenerator
from chatlib import cli, env_helper

if __name__ == "__main__":
    # Init OpenAI API
    load_dotenv(path.join(getcwd(), ".env"))
    openai.api_key = env_helper.get_env_variable('OPENAI_API_KEY')
    AzureLlama2Environment.set_host(env_helper.get_env_variable('AZURE_LLAMA2_HOST'))
    AzureLlama2Environment.set_key(env_helper.get_env_variable('AZURE_LLAMA2_KEY'))

    user_name = input("Please enter child's name: ").strip()
    user_age = int(input("Please enter child's age: ").strip())
    locale = int(input("Put number for your locale. 1. Korean (default), 2. English   : "))
    locale = ChatbotLocale.English if locale == 2 else ChatbotLocale.Korean

    child_agent_model = int(input("Put number for the model of a child agent. 1. GPT (default), 2. Llama2   : "))
    child_agent_generator = Llama2ResponseGenerator if child_agent_model == 2 else ChatGPTResponseGenerator

    asyncio.run(cli.run_auto_chat_loop(
        EmotionChatbotResponseGenerator(user_name=user_name, user_age=user_age, locale=locale, verbose=True),
        child_agent_generator(base_instruction=f"""
You are a {user_age}-year-old Korean child named {user_name} who is shy and worried. Your main concern is to mitigate any potential conflicts with your peers. You prefer avoiding any conflicts to asserting your opinions. You always worry about how others think about you. You prioritize others' views over your own. You do not share your concerns with anyone, including your parents.            
            Speaking Rules:
            {"1. Use a simple, informal Korean like talking to a peer friend." if locale is ChatbotLocale.Korean else "1. Use a simple, informal English like talking to a peer friend."}
            2. Say three sentences at the most each time.  
            3. Do not ask question unless you do not understand certain emotion words.  
                                        """),
        max_turns=30
    ))