#!/usr/bin/env python
"""
Comprehensive test for the booking flow with complex date/time formats
"""

import asyncio
import logging
from src.bot.chatbot import CalendarAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_complete_booking_flow():
    """Test a complete booking flow with complex date/time formats"""
    try:
        # Initialize the calendar agent
        agent = CalendarAgent()
        await agent.initialize()
        
        # Set user email in conversation context
        agent.conversation_context["current_user_email"] = "test@example.com"
        
        print("\n===== Testing Complete Booking Flow =====")
        
        # Step 1: Initial booking request with complex date/time format
        booking_request = "book me on Monday, May 19, 2025 at 9:00 AM PST, my name: jisoo, reason: offer review, 30minute meeting"
        print(f"\nUSER: {booking_request}")
        
        response = await agent.process_message(booking_request)
        print(f"BOT: {response.get('response', 'No response')}")
        
        # Step 2: Check availability for a specific date
        availability_request = "What times are available on May 20, 2025?"
        print(f"\nUSER: {availability_request}")
        
        response = await agent.process_message(availability_request)
        print(f"BOT: {response.get('response', 'No response')}")
        
        # Step 3: Book using a time from availability
        follow_up_request = "Book me at 3:00 PM that day"
        print(f"\nUSER: {follow_up_request}")
        
        response = await agent.process_message(follow_up_request)
        print(f"BOT: {response.get('response', 'No response')}")
        
        # Clean up
        await agent.cleanup()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_complete_booking_flow()

if __name__ == "__main__":
    asyncio.run(main()) 