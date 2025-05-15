"""
Test script to directly test the api_service module
"""
import os
from dotenv import load_dotenv
import sys
import json
import traceback

# Force reload of environment variables
os.environ.clear()
load_dotenv(override=True)

print("\n=== Testing API Service ===")
print(f"CHATBOT_API_URL: {os.getenv('CHATBOT_API_URL')}")

try:
    # Import our api_service module
    print("Importing api_service module...")
    from api_service import send_message

    # Test sending a message
    print("\nSending test message...")
    response = send_message(
        message="test message from script",
        user_email="test@example.com",
        conversation_id="test-script-convo"
    )
    
    # Print response
    print("\nResponse:")
    print(json.dumps(response, indent=2))
except Exception as e:
    print(f"\nERROR: {str(e)}")
    print(traceback.format_exc()) 