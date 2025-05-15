#!/usr/bin/env python
"""
Test script for the Cal.com Scheduler Agent chatbot.
This script tests the enhanced chatbot functionality, focusing on intent identification,
conversation state management, and function calling.
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"chatbot_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bot.chatbot import CalendarAgent
from src.utils.config import OPENAI_API_KEY

async def run_test():
    """Run a basic test of the chatbot functionality."""
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key is missing, please set it in the environment variables.")
        return
    
    logger.info("Initializing Calendar Agent for testing...")
    agent = CalendarAgent()
    
    try:
        # Initialize the agent
        await agent.initialize()
        logger.info("Calendar Agent initialized, beginning test scenarios...")
        
        # Test the chatbot with the built-in test method
        test_email = "test@example.com"
        logger.info(f"Running standard test flow with user email: {test_email}")
        test_results = await agent.test_chat(user_email=test_email, verbose=True)
        
        # Save test results to a file
        results_file = f"chatbot_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        logger.info(f"Test results saved to {results_file}")
        
        # Test custom scenarios
        logger.info("Testing specific conversation scenarios...")
        
        # Scenario 1: Complex multi-turn conversation
        logger.info("\n===== SCENARIO 1: Multi-turn booking ======")
        await agent.initialize()  # Reset the agent
        
        # First message - greeting and intent
        response1 = await agent.process_message(
            "Hi there! I need to schedule a couple of meetings next week.", 
            user_email="complex@example.com"
        )
        print(f"USER: Hi there! I need to schedule a couple of meetings next week.")
        print(f"BOT: {response1['response']}")
        print(f"INTENT: {response1.get('intent', 'unknown')}, ACTION: {response1.get('action_taken', 'none')}")
        
        # Second message - specific booking request
        response2 = await agent.process_message(
            "I'd like to book a meeting on Monday at 10am for a team discussion.", 
            user_email="complex@example.com"
        )
        print(f"USER: I'd like to book a meeting on Monday at 10am for a team discussion.")
        print(f"BOT: {response2['response']}")
        print(f"INTENT: {response2.get('intent', 'unknown')}, ACTION: {response2.get('action_taken', 'none')}")
        
        # Third message - modification request
        response3 = await agent.process_message(
            "Actually, can we make that Tuesday at 2pm instead?", 
            user_email="complex@example.com"
        )
        print(f"USER: Actually, can we make that Tuesday at 2pm instead?")
        print(f"BOT: {response3['response']}")
        print(f"INTENT: {response3.get('intent', 'unknown')}, ACTION: {response3.get('action_taken', 'none')}")
        
        print("\nScenario 1 Conversation Context:")
        print(json.dumps(agent.conversation_context, indent=2))
        
        # Summary stats
        print(f"\nTotal messages processed: {agent.conversation_context['total_messages']}")
        print(f"Actions attempted: {agent.conversation_context['total_actions']}")
        print(f"Last detected intent: {agent.conversation_context['last_intent']}")
        
        logger.info("Test complete.")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
    finally:
        # Clean up resources
        await agent.cleanup()
        logger.info("Test cleanup completed.")

if __name__ == "__main__":
    asyncio.run(run_test()) 