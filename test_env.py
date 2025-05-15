import os
from dotenv import load_dotenv

# Force reload of environment variables
os.environ.clear()
load_dotenv(override=True)

print(f"CHATBOT_API_URL: {os.getenv('CHATBOT_API_URL')}") 