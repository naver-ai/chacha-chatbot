from os import path, getcwd

from dotenv import find_dotenv, set_key

#Create env files if not exist ========================================================

env_file = find_dotenv()
if not path.exists(env_file):
    env_file = open(path.join(getcwd(), '.env'), 'w', encoding='utf-8')
    env_file.close()
    env_file = find_dotenv()

while True:
    openai_api_key = input("Enter OpenAI API Key: ").strip()

    if openai_api_key is not None and len(openai_api_key) > 0:
        set_key(env_file, "OPENAI_API_KEY", openai_api_key)
        break

print("Wrote .env file.")