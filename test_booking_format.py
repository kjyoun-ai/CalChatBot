#!/usr/bin/env python
"""
Test script for testing time format handling in booking functions
"""

import asyncio
import logging
from src.bot.chatbot import CalendarAgent
from src.bot.openai_integration import OpenAIFunctionCaller

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_openai_time_normalize():
    """Test the _normalize_time_format method in OpenAIFunctionCaller"""
    print("\n===== Testing OpenAI Time Normalization =====")
    
    # Create an instance of OpenAIFunctionCaller
    caller = OpenAIFunctionCaller()
    
    # Test various time formats
    test_cases = [
        "9:00 AM PST",
        "9:00 at AM PST",
        "3pm",
        "15:00",
        "at 3pm",
        "morning",
        "9:00AM EST",
        "3:00 PM",
        "9 AM",
        "9AM",
        "at 9:00 AM PST"
    ]
    
    for test_case in test_cases:
        normalized = caller._normalize_time_format(test_case)
        print(f"'{test_case}' → '{normalized}'")

async def test_bot_booking():
    """Test the booking functionality with various time formats"""
    print("\n===== Testing Bot Booking with Various Time Formats =====")
    
    # Initialize the calendar agent
    agent = CalendarAgent()
    await agent.initialize()
    
    # Test booking with various time formats
    test_times = [
        "2025-05-19",  # Date only
        "9:00 AM PST",  # The problematic format
        "Jisoo",        # Name
        "offer review"  # Reason
    ]
    
    try:
        # Test a direct call to book_meeting with the problematic format
        print("\nTesting direct book_meeting call...")
        result = await agent.book_meeting(
            date="2025-05-19",
            time="9:00 AM PST",
            name="Jisoo",
            reason="offer review",
            duration=30
        )
        print(f"Result: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        # Test via message processing
        print("\nTesting via process_message...")
        response = await agent.process_message("book me on Monday, May 19, 2025 at 9:00 AM PST, my name: jisoo, reason: offer review, 30minute meeting")
        print(f"Response: {response.get('response', 'No response')}")
        
        # Clean up
        await agent.cleanup()
    except Exception as e:
        print(f"Error during testing: {e}")

async def main():
    """Run all tests"""
    try:
        await test_openai_time_normalize()
        await test_bot_booking()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 