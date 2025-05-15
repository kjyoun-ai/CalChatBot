#!/usr/bin/env python
"""
Test script for availability slots
"""

import asyncio
import logging
from src.bot.chatbot import CalendarAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    try:
        # Initialize the calendar agent
        agent = CalendarAgent()
        await agent.initialize()
        
        # Test the availability check
        print("Testing availability check...")
        response = await agent.process_message("when is available on May 17th, 2025?")
        print("\nResponse:")
        print(response.get("response", "No response"))
        print("\nDetails:")
        print(response.get("details", {}))
        
        # Test another availability check
        print("\nTesting another availability check...")
        response = await agent.process_message("okay when is available on that day?")
        print("\nResponse:")
        print(response.get("response", "No response"))
        print("\nDetails:")
        print(response.get("details", {}))
        
        # Clean up
        await agent.cleanup()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 