#!/usr/bin/env python
"""
Test script for the Chatbot handling of get_available_slots
"""

import asyncio
from src.bot.chatbot import CalendarAgent

async def main():
    print("Initializing agent...")
    agent = CalendarAgent()
    
    # Initialize the agent and add a system message
    agent.conversation_history.append({
        "role": "system", 
        "content": "You are a calendar scheduling assistant."
    })
    
    # Test availability question
    test_message = "Get available slot for 30 minute that is soonest available."
    print(f"\nTest message: {test_message}")
    
    response = await agent.process_message(test_message)
    
    print("\nResponse:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main()) 