#!/usr/bin/env python
"""
Test script to verify intent detection and the conversation flow from availability to booking
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from src.api.cal_api import CalAPIClient
from src.bot.chatbot import CalendarAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("intent_flow_test")

async def test_intent_and_flow():
    """Test intent detection and the conversation flow"""
    try:
        # Initialize the chat agent
        agent = CalendarAgent()
        await agent.initialize()
        
        # Set user email in conversation context
        agent.conversation_context["current_user_email"] = "test@example.com"
        
        # Get tomorrow's date for testing
        tomorrow = datetime.now() + timedelta(days=1)
        test_date = tomorrow.strftime("%Y-%m-%d")
        
        print("\n===== Intent Detection and Conversation Flow Test =====")
        
        # Test 1: Check intent detection for availability
        print("\nTEST 1: Intent detection for availability check")
        test_messages = [
            "What times do you have available?",
            "When can I schedule a meeting?",
            "Do you have any slots tomorrow?",
            "Show me your calendar for next Monday"
        ]
        
        for msg in test_messages:
            print(f"\nUSER: {msg}")
            response = await agent.process_message(msg)
            print(f"BOT: {response.get('response')}")
            
            # Check if we received available time slots or a follow-up about date
            if any(x in response.get('response', '').lower() for x in ["available", "slot", "time", "date"]):
                print("✓ Correctly recognized availability intent")
            else:
                print("✗ Failed to recognize availability intent")
        
        # Test 2: Test intent detection for booking
        print("\nTEST 2: Intent detection for booking")
        booking_messages = [
            f"I want to book a meeting on {test_date}",
            "Let's set up a call for tomorrow at 2pm",
            "I'd like to schedule a 30 minute appointment",
            "Book me in for 9am PST"
        ]
        
        for msg in booking_messages:
            print(f"\nUSER: {msg}")
            response = await agent.process_message(msg)
            print(f"BOT: {response.get('response')}")
            
            # Check if the response indicates booking intent was detected
            if any(x in response.get('response', '').lower() for x in ["book", "schedule", "appointment", "confirm"]):
                print("✓ Correctly recognized booking intent")
            else:
                print("✗ Failed to recognize booking intent")
        
        # Test 3: Test the complete flow from availability check to booking
        # Reset conversation history to start fresh
        agent.reset_conversation()
        agent.conversation_context["current_user_email"] = "test@example.com"
        
        print("\nTEST 3: Full conversation flow from availability to booking")
        
        # Step 1: Ask about availability
        flow_test = [
            f"What times are available on {test_date}?",  # Check availability
            "How about at 9:30 AM PST?",                 # Try to book a specific time
            "Yes, let's book that time"                   # Confirm booking
        ]
        
        for i, msg in enumerate(flow_test):
            print(f"\nUSER ({i+1}/{len(flow_test)}): {msg}")
            response = await agent.process_message(msg)
            print(f"BOT: {response.get('response')}")
            
            # Check for appropriate response based on message sequence
            if i == 0:  # First message - should return available slots
                if "available" in response.get('response', '').lower():
                    print("✓ Correctly provided availability information")
                else:
                    print("✗ Failed to provide availability information")
            elif i == 1:  # Second message - should acknowledge time request
                if any(x in response.get('response', '').lower() for x in ["9:30", "book", "confirm"]):
                    print("✓ Correctly processed specific time request")
                else:
                    print("✗ Failed to process specific time request")
            elif i == 2:  # Third message - should attempt to book or explain why it can't
                if any(x in response.get('response', '').lower() for x in ["booked", "confirmed", "scheduled", "available", "could not"]):
                    print("✓ Provided appropriate booking result")
                else:
                    print("✗ Failed to provide booking result")
        
        # Test 4: Test intent memory retention
        print("\nTEST 4: Intent memory retention")
        
        # Reset conversation history
        agent.reset_conversation()
        agent.conversation_context["current_user_email"] = "test@example.com"
        
        conversation = [
            "I want to book a meeting",
            "Tomorrow",
            "In the morning",
            "10 AM",
            "For about an hour"
        ]
        
        for i, msg in enumerate(conversation):
            print(f"\nUSER ({i+1}/{len(conversation)}): {msg}")
            response = await agent.process_message(msg)
            print(f"BOT: {response.get('response')}")
            
            # Check if the follow-up requests retain context
            if i > 0 and any(x in response.get('response', '').lower() for x in ["book", "schedule", "time", "appointment"]):
                print("✓ Context retained between messages")
            elif i == 0:
                print("(Initial message - no context to retain yet)")
        
        # Clean up
        await agent.cleanup()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_intent_and_flow()

if __name__ == "__main__":
    asyncio.run(main()) 