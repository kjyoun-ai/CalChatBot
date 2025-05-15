import os
from dotenv import load_dotenv

# Force reload of environment variables
os.environ.clear()
load_dotenv(override=True)

import requests
import traceback

# Use environment variables for configuration
API_BASE_URL = os.getenv("CHATBOT_API_URL", "http://localhost:8000")
API_KEY = os.getenv("CHATBOT_API_KEY", "test-api-key")

# Write debug info to a file
with open("debug.log", "a") as f:
    f.write(f"API_BASE_URL = {API_BASE_URL}\n")
    f.write(f"API_KEY = {API_KEY}\n")

HEADERS = {"X-API-Key": API_KEY}


def send_message(message: str, user_email: str, conversation_id: str = None):
    """
    Send a message to the chatbot backend and return the response.
    """
    url = f"{API_BASE_URL}/chat"
    payload = {
        "message": message,
        "user_email": user_email,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    # Write debug info before making the request
    with open("debug.log", "a") as f:
        f.write(f"\nSending request to: {url}\n")
        f.write(f"Headers: {HEADERS}\n")
        f.write(f"Payload: {payload}\n")
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=30)
        
        # Write debug info about the response
        with open("debug.log", "a") as f:
            f.write(f"Response status: {response.status_code}\n")
            f.write(f"Response headers: {dict(response.headers)}\n")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        
        # Write detailed error info
        with open("debug.log", "a") as f:
            f.write(f"Error: {error_message}\n")
            f.write(f"Traceback: {traceback.format_exc()}\n")
        
        return {"error": error_message}
    except Exception as e:
        error_message = str(e)
        
        # Write detailed error info
        with open("debug.log", "a") as f:
            f.write(f"Unexpected error: {error_message}\n")
            f.write(f"Traceback: {traceback.format_exc()}\n")
        
        return {"error": error_message}


def get_conversation_messages(conversation_id: str):
    """
    Retrieve the message history for a conversation.
    """
    url = f"{API_BASE_URL}/api/conversations/{conversation_id}/messages"
    
    # Write debug info before making the request
    with open("debug.log", "a") as f:
        f.write(f"\nFetching messages from: {url}\n")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        error_message = str(e)
        
        # Write error info
        with open("debug.log", "a") as f:
            f.write(f"Error fetching messages: {error_message}\n")
        
        return {"error": error_message} 