from os import path, getcwd
from typing import Callable

from dotenv import find_dotenv, set_key
import questionary
from questionary import prompt


# Create env files if not exist ========================================================

def make_non_empty_string_validator(msg: str) -> Callable:
    return lambda text: True if len(text.strip()) > 0 else msg


env_file = find_dotenv()
if not path.exists(env_file):
    env_file = open(path.join(getcwd(), '.env'), 'w', encoding='utf-8')
    env_file.close()
    env_file = find_dotenv()

configure_openai = questionary.confirm("Would you like to configure OpenAI GPT?").ask()

if configure_openai:
    openai_api_key = questionary.text("Enter OpenAI API Key:",
                                      validate=make_non_empty_string_validator("Please enter a valid key.")).ask().strip()
    set_key(env_file, "OPENAI_API_KEY", openai_api_key)

configure_llama = questionary.confirm("Would you like to configure Azure Llama2?").ask()

if configure_llama:
    llama_questions = [
        {
            'type': 'text',
            'name': 'host',
            'message': 'Enter Azure Llama2 target address:',
            'validate': make_non_empty_string_validator("Please enter a valid address.")
        },
        {
            'type': 'text',
            'name': 'key',
            'message': 'Enter Azure Llama2 key:',
            'validate': make_non_empty_string_validator("Please enter a valid key.")
        },
    ]

    answers = prompt(llama_questions)

    set_key(env_file, "AZURE_LLAMA2_HOST", answers['host'].strip())
    set_key(env_file, "AZURE_LLAMA2_KEY", answers['key'].strip())


configure_google = questionary.confirm("Would you like to configure Google API?").ask()

if configure_google:
    google_api_key = questionary.text("Enter Google API Key:",
                                      validate=make_non_empty_string_validator(
                                          "Please enter a valid key.")).ask().strip()
    set_key(env_file, "GOOGLE_API_KEY", google_api_key)

print("Finished configuration.")
