#!/usr/bin/env python
"""
Test script for the complete booking flow with availability check
"""

import asyncio
import logging
from datetime import datetime, timedelta
from src.bot.chatbot import CalendarAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_booking_with_availability_check():
    """Test booking with proper availability check"""
    try:
        # Initialize the calendar agent
        agent = CalendarAgent()
        await agent.initialize()
        
        # Set user email in conversation context
        agent.conversation_context["current_user_email"] = "test@example.com"
        
        print("\n===== Testing Booking Flow With Availability Check =====")
        
        # Get tomorrow's date for testing
        tomorrow = datetime.now() + timedelta(days=1)
        test_date = tomorrow.strftime("%Y-%m-%d")
        
        # Test 1: Try booking at a time that's outside of available hours (too early)
        outside_hours_time = "10:00 AM"
        print(f"\nTEST 1: Booking at {outside_hours_time} on {test_date} (Outside Available Hours)")
        result = await agent.book_meeting(
            date=test_date,
            time=outside_hours_time,
            name="Test User",
            reason="Testing outside hours",
            skip_availability_check=False  # Enable availability check
        )
        
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        
        # Test 2: Get available slots for the date
        print(f"\nTEST 2: Getting Available Slots for {test_date}")
        slots_result = await agent.get_available_slots(date_str=test_date)
        
        # Show available slots
        if slots_result.get("status") == "success":
            slots = slots_result.get("available_slots", [])
            print(f"Found {len(slots)} available slots")
            
            # Display the first 3 slots
            for i, slot in enumerate(slots[:3]):
                print(f"Slot {i+1}: {slot.get('display')}")
            
            # Test 3: Try booking at an available time
            if slots:
                available_slot = slots[0]
                available_time = available_slot.get("formatted_time")
                
                print(f"\nTEST 3: Booking at {available_time} on {test_date} (Within Available Hours)")
                booking_result = await agent.book_meeting(
                    date=test_date,
                    time=available_time,
                    name="Test User",
                    reason="Testing within available hours",
                    skip_availability_check=False  # Enable availability check
                )
                
                print(f"Status: {booking_result.get('status')}")
                print(f"Message: {booking_result.get('message')}")
        else:
            print(f"Error getting available slots: {slots_result.get('message')}")
        
        # Test 4: Use process_message to test the entire flow
        print("\nTEST 4: Testing via process_message (with booking intent detection)")
        
        # First message - intent detection and date extraction
        booking_message = f"I'd like to book a meeting on {test_date}"
        print(f"USER: {booking_message}")
        response = await agent.process_message(booking_message)
        print(f"BOT: {response.get('response')}")
        
        # Second message - with a time that's likely outside available hours
        time_message = "How about at 9:00 AM?"
        print(f"USER: {time_message}")
        response = await agent.process_message(time_message)
        print(f"BOT: {response.get('response')}")
        
        # Third message - asking for available times
        availability_message = "What times are available on that day?"
        print(f"USER: {availability_message}")
        response = await agent.process_message(availability_message)
        print(f"BOT: {response.get('response')}")
        
        # Clean up
        await agent.cleanup()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_booking_with_availability_check()

if __name__ == "__main__":
    asyncio.run(main()) 