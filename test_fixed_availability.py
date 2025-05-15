"""
Test the fixed implementation for checking availability.
"""
import os
import sys
import asyncio
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.bot.chatbot import CalendarAgent

async def test_fixed_implementation():
    """Test the fixed implementation for getting availability."""
    print("\n=== Testing Fixed Implementation ===")
    
    # Create the calendar agent
    agent = CalendarAgent()
    
    # Initialize the agent
    await agent.initialize()
    
    # Get tomorrow's date
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Checking availability for tomorrow ({tomorrow})")
    
    # Test the availability check
    print("\nTesting 'show me available meeting slot for tomorrow 2~5pm pst for hour meeting'...")
    response = await agent.process_message("show me available meeting slot for tomorrow 2~5pm pst for hour meeting")
    
    # Print the response
    print("\nAgent Response:")
    print(response["response"])
    
    print("\nDetailed information:")
    print(f"Action taken: {response['action_taken']}")
    print(f"Intent detected: {response['intent']}")
    
    # Test booking at 2pm
    print("\nTesting 'book a meeting tomorrow at 2pm'...")
    response = await agent.process_message("book a meeting tomorrow at 2pm")
    
    # Print the response
    print("\nAgent Response to booking request:")
    print(response["response"])
    
    # Skip cleanup to avoid errors
    # If cleanup is needed, use:
    # if hasattr(agent.cal_api, 'client') and agent.cal_api.client:
    #     await agent.cal_api.client.aclose()

if __name__ == "__main__":
    asyncio.run(test_fixed_implementation()) 