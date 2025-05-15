#!/usr/bin/env python
"""
Test script to verify time format handling in the Cal API
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from src.api.cal_api import CalAPIClient
from src.bot.chatbot import CalendarAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_time_formats():
    """Test various time formats for booking"""
    try:
        # Initialize the chat agent
        agent = CalendarAgent()
        await agent.initialize()
        
        # Set user email in conversation context
        agent.conversation_context["current_user_email"] = "test@example.com"
        
        # Get tomorrow's date for testing
        tomorrow = datetime.now() + timedelta(days=1)
        test_date = tomorrow.strftime("%Y-%m-%d")
        
        print("\n===== Testing Various Time Formats =====")
        
        # Test different time formats
        time_formats = [
            "9:00 AM",
            "09:00 AM",
            "9:00AM",
            "9:00 AM PST",
            "9:00AM PST",
            "9am",
            "9AM",
            "0900",
            "09:00",
            "17:00 UTC"  # This is equivalent to 9:00 AM PST
        ]
        
        for time_format in time_formats:
            print(f"\nTesting time format: '{time_format}'")
            
            # Attempt to book with this time format
            result = await agent.book_meeting(
                date=test_date,
                time=time_format,
                name="Test User",
                reason=f"Testing time format: {time_format}",
                skip_availability_check=False
            )
            
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            
            # If there's a different error than availability, show it
            if result.get('status') == 'error' and 'not available' not in result.get('message', ''):
                print(f"ERROR: {result.get('technical_details', 'No details')}")
        
        # Test direct message parsing
        print("\n===== Testing Time Format Parsing Through Messages =====")
        
        # Test a few messages with different time formats
        for time_format in ["9:00 AM PST", "5pm", "3:30 PM EST"]:
            message = f"I'd like to book a meeting on {test_date} at {time_format}"
            print(f"\nUSER: {message}")
            
            response = await agent.process_message(message)
            print(f"BOT: {response.get('response')}")
        
        # Clean up
        await agent.cleanup()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_time_formats()

if __name__ == "__main__":
    asyncio.run(main()) 