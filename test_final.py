#!/usr/bin/env python3
"""
Final test for the Cal.com scheduling agent.
This test verifies all the improvements we've made to the chatbot:
1. Immediate responses without requiring confirmation
2. Correct date parsing in various formats
3. Graceful handling of API errors
4. Proper extraction of available time slots from the Cal.com API response
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from src.bot.chatbot import CalendarAgent
from src.api.cal_api import CalAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_immediate_response():
    """Test that the bot provides immediate responses without requiring confirmation."""
    print("\n===== Testing Immediate Response =====")
    
    # Initialize the CalendarAgent
    agent = CalendarAgent()
    await agent.initialize()
    
    # Test messages with different date formats
    test_messages = [
        {
            "message": "Find the earliest available time for tomorrow",
            "description": "Tomorrow's date format",
            "expected_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        },
        {
            "message": "What's the earliest 30-minute slot on 2025-05-15?",
            "description": "ISO date format (YYYY-MM-DD)",
            "expected_date": "2025-05-15"
        },
        {
            "message": "Find me a time for 2025 5/15 earliest time for 30 min meeting pst time zone",
            "description": "Custom date format (YYYY M/D)",
            "expected_date": "2025-05-15"
        },
        {
            "message": "What's the earliest 15-minute meeting slot available on 05/15/2025?",
            "description": "US date format (MM/DD/YYYY)",
            "expected_date": "2025-05-15"
        }
    ]
    
    # Run each test case
    for test_case in test_messages:
        print(f"\n{test_case['description']}: '{test_case['message']}'")
        
        # Get the response - expecting a string
        response = await agent.process_message(test_case["message"])
        
        # Print the bot's response
        print(f"Bot Response: {response}")
        
        # Check if this was a successful test
        if "earliest available" in response.lower() or "connection issues" in response.lower():
            print("✅ PASS: Bot provided immediate response without waiting for confirmation")
        elif "I will now check" in response.lower() or "let me find" in response.lower():
            print("❌ FAIL: Bot did not provide immediate results, asks for confirmation instead")
        else:
            print("❓ UNKNOWN: Bot provided an unexpected response")
        
        # Verify date parsing - check conversation history for expected date
        conversation_history_str = str(agent.conversation_history)
        if test_case["expected_date"] in conversation_history_str:
            print(f"✅ PASS: Bot correctly parsed the date {test_case['expected_date']}")
        else:
            print(f"❌ FAIL: Bot did not correctly parse the date {test_case['expected_date']}")
    
    print("\n===== Immediate Response Test Complete =====")

async def test_api_interaction():
    """Test interaction with the Cal.com API."""
    print("\n===== Testing Cal.com API Interaction =====")
    
    try:
        # Initialize the Cal.com API client
        cal_api = CalAPIClient()
        
        # Test API connection
        print("Testing API connection...")
        connection_result = await cal_api.test_api_connection()
        print(f"API Connection: {'✅ Success' if connection_result else '❌ Failed'}")
        
        if connection_result:
            # Get available event types
            print("Checking available event types...")
            event_types_result = await cal_api.check_available_event_types()
            if event_types_result.get("status") == "success":
                print(f"✅ Successfully retrieved event types: {event_types_result}")
            else:
                print(f"❌ Failed to retrieve event types: {event_types_result}")
            
            # Try to get availability for a specific date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"Getting availability for {tomorrow}...")
            availability_result = await cal_api.get_availability("2472559", tomorrow)
            if availability_result.get("status") == "success":
                print(f"✅ Successfully retrieved availability: {availability_result}")
            else:
                print(f"❌ Failed to retrieve availability: {availability_result}")
    except Exception as e:
        print(f"❌ Error during API testing: {str(e)}")
    
    print("\n===== API Interaction Test Complete =====")

async def test_error_handling():
    """Test the bot's ability to handle API errors gracefully."""
    print("\n===== Testing Error Handling =====")
    
    # Initialize the CalendarAgent
    agent = CalendarAgent()
    await agent.initialize()
    
    # Test with intentionally bad API key
    # Save the real API key
    real_api_key = agent.cal_api.api_key
    
    try:
        print("Testing with invalid API key...")
        agent.cal_api.api_key = "invalid_api_key"
        agent.cal_api.headers["Authorization"] = f"Bearer invalid_api_key"
        
        # Send a message that requires API access
        message = "Find the earliest available time tomorrow"
        print(f"Sending message: '{message}'")
        
        response = await agent.process_message(message)
        print(f"Bot Response: {response}")
        
        # Check if the response correctly indicates a connection problem
        if "connection issues" in response.lower() or "error" in response.lower():
            print("✅ PASS: Bot handled API error gracefully")
        else:
            print("❌ FAIL: Bot did not handle API error gracefully")
    except Exception as e:
        print(f"❌ Exception during error handling test: {str(e)}")
    finally:
        # Restore the real API key
        agent.cal_api.api_key = real_api_key
        agent.cal_api.headers["Authorization"] = f"Bearer {real_api_key}"
    
    print("\n===== Error Handling Test Complete =====")

async def main():
    """Run all the tests."""
    print("===== Starting Cal.com Scheduling Agent Tests =====\n")
    
    await test_immediate_response()
    await test_api_interaction()
    await test_error_handling()
    
    print("\n===== All Tests Complete =====")

if __name__ == "__main__":
    asyncio.run(main()) 