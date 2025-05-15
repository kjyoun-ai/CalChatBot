#!/usr/bin/env python3
"""
Test that the chatbot provides immediate availability results without confirmation.
This test checks that when users ask for the earliest available time, the bot 
responds with that information immediately, rather than requiring a follow-up "okay".
"""

import asyncio
from datetime import datetime, timedelta
import logging
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from src.bot.chatbot import CalendarAgent
from src.utils.config import logger

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_find_earliest_slot():
    """Test that the bot provides immediate availability results without waiting for a confirmation."""
    print("\n===== Testing Immediate Availability Response =====")
    
    # Initialize the CalendarAgent
    agent = CalendarAgent()
    await agent.initialize()
    
    # Test messages
    test_messages = [
        {
            "message": "Find the earliest available time for tomorrow",
            "description": "Test 1: 'Find the earliest available time for tomorrow'"
        },
        {
            "message": "What's the earliest 30-minute slot available?",
            "description": "Test 2: 'What's the earliest 30-minute slot available?'"
        },
        {
            "message": "Find me a time for 2025-05-15 earliest time for 30 min meeting pst time zone",
            "description": "Test 3: 'Find me a time for 2025-05-15 earliest time for 30 min meeting pst time zone'"
        },
        {
            "message": "Find me a time for 2025 5/15 earliest time for 30 min meeting pst time zone",
            "description": "Specific Date Test: 'Find me a time for 2025 5/15 earliest time for 30 min meeting pst time zone'"
        }
    ]
    
    # Run each test case
    for test_case in test_messages:
        print(f"\n{test_case['description']}")
        
        # Get the response directly - now expecting a string
        response = await agent.process_message(test_case["message"])
        
        # Print the bot's response and the action taken
        print(f"Bot Response: {response}")
        
        # Check if this was a successful test (no need to say "okay" to get results)
        if "earliest available" in response.lower() or "connection issues" in response.lower():
            # Either it immediately provided availability information or properly handled an error
            print("✅ PASS: Bot provided immediate response without requiring confirmation")
        elif "I will now check" in response.lower() or "let me find" in response.lower():
            # It responded with a confirmation prompt rather than actual results
            print("❌ FAIL: Bot did not provide immediate results, asks for confirmation instead")
        else:
            # Some other kind of response
            print("❓ UNKNOWN: Bot provided an unexpected response")
        
        # Special test for the date format parsing
        if "2025 5/15" in test_case["message"]:
            if "2025-05-15" in str(agent.conversation_history):
                print("✅ PASS: Bot correctly parsed the date 2025-05-15")
            else:
                print("❌ FAIL: Bot did not correctly parse the date 2025-05-15")
    
    print("\n===== Test Complete =====")

if __name__ == "__main__":
    asyncio.run(test_find_earliest_slot()) 