from os import path, getcwd

from chatlib.global_config import GlobalConfig
from chatlib.llm.integration import GPTChatCompletionAPI
from dotenv import find_dotenv, set_key
from app.models.HyperClovaXAPI import HyperClovaXAPI

#Create env files if not exist ========================================================

if __name__ == "__main__":
    GlobalConfig.is_cli_mode = True
    GPTChatCompletionAPI().assert_authorize()
    HyperClovaXAPI().assert_authorize()

print("Wrote .env file.")