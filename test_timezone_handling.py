#!/usr/bin/env python
"""
Comprehensive test script to verify timezone handling in the Cal.com integration
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from src.api.cal_api import CalAPIClient
from src.bot.chatbot import CalendarAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("timezone_test")

async def test_timezone_handling():
    """Test timezone handling for availability checks and booking"""
    try:
        # Initialize the chat agent
        agent = CalendarAgent()
        await agent.initialize()
        
        # Set user email in conversation context
        agent.conversation_context["current_user_email"] = "test@example.com"
        
        # Get tomorrow's date for testing
        tomorrow = datetime.now() + timedelta(days=1)
        test_date = tomorrow.strftime("%Y-%m-%d")
        
        print("\n===== Timezone Handling Test =====")
        
        # Test 1: Check availability for tomorrow
        print("\nTEST 1: Checking availability for tomorrow")
        slots_result = await agent.get_available_slots(date_str=test_date)
        
        if slots_result.get("status") == "success":
            slots = slots_result.get("available_slots", [])
            print(f"Found {len(slots)} available slots")
            
            # Display the first 3 slots and their timezone information
            for i, slot in enumerate(slots[:3]):
                print(f"Slot {i+1}: {slot.get('iso')} → {slot.get('display')} (formatted as {slot.get('formatted_time')})")
                
            # Test 2: Try with timezone specified correctly in PST (should succeed in availability check)
            if slots:
                # Extract the hour from the first available slot and add time zone
                slot_display = slots[0].get('display', '')
                time_part = slots[0].get('formatted_time', '')
                
                print(f"\nTEST 2: Parsing time with PST timezone: '{time_part} PST'")
                
                # Get the available slot, format it as "9:00 AM PST"
                pst_formatted_time = f"{time_part} PST"
                
                # Check if this time is available
                availability_result = await agent.cal_api.is_time_available(
                    event_type_id=slots[0].get("event_type_id"),
                    datetime_str=slots[0].get("iso")
                )
                
                print(f"Checking if {pst_formatted_time} is available ({slots[0].get('iso')}): {availability_result}")
                
                # Test 3: Try booking with the timezone
                print(f"\nTEST 3: Booking with timezone in time format: {pst_formatted_time}")
                booking_result = await agent.book_meeting(
                    date=test_date,
                    time=pst_formatted_time,
                    name="Test User",
                    reason="Testing timezone handling",
                    skip_availability_check=False  # Enable availability check
                )
                
                print(f"Status: {booking_result.get('status')}")
                print(f"Message: {booking_result.get('message')}")
                
                # If there's an error, check if it's the availability issue
                if booking_result.get('status') == 'error':
                    if 'not available' in booking_result.get('message', ''):
                        print("✓ Error handling correctly indicated unavailability")
                        # Check if alternative slots are suggested
                        if 'Alternative available times' in booking_result.get('message', ''):
                            print("✓ Alternative slots are suggested in error message")
                        else:
                            print("✗ No alternative slots suggested in error message")
                    else:
                        print(f"Technical details: {booking_result.get('technical_details', 'None')}")
                else:
                    print("✓ Booking successful with timezone specified")
            else:
                print("No available slots found for testing")
        else:
            print(f"Error getting available slots: {slots_result.get('message')}")
        
        # Test 4: Test full conversation flow
        print("\nTEST 4: Testing full conversation flow with timezone handling")
        
        # Start by asking about availability
        avail_message = f"What times are available tomorrow?"
        print(f"USER: {avail_message}")
        response = await agent.process_message(avail_message)
        print(f"BOT: {response.get('response')}")
        
        # Follow up with booking intent with timezone
        if "Found" in response.get('response', '') or "available" in response.get('response', ''):
            booking_message = f"I'd like to book at 9:30 AM PST"
            print(f"USER: {booking_message}")
            response = await agent.process_message(booking_message)
            print(f"BOT: {response.get('response')}")
        
        # Clean up
        await agent.cleanup()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_timezone_handling()

if __name__ == "__main__":
    asyncio.run(main()) 