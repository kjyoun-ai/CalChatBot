#!/usr/bin/env python3
"""
Test Cal.com API connection and event type retrieval.
This test checks that we can successfully connect to the Cal.com API
and retrieve available event types using the new API key.
"""

import asyncio
import json
import logging
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from src.api.cal_api import CalAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cal_api_connection():
    """Test connection to Cal.com API and event type retrieval."""
    logger.info("===== Testing Cal.com API Connection =====")
    
    # Initialize the Cal.com API client
    cal_api = CalAPIClient()
    
    # Test API connection
    logger.info("Testing API connection...")
    connection_result = await cal_api.test_api_connection()
    logger.info(f"Connection test result: {connection_result}")
    
    # Check available event types
    logger.info("Checking available event types...")
    event_types_result = await cal_api.check_available_event_types()
    logger.info(f"Event types result status: {event_types_result.get('status')}")
    
    if event_types_result.get('status') == 'success':
        event_types = event_types_result.get('event_types', [])
        logger.info(f"Found {len(event_types)} event types:")
        for et in event_types:
            logger.info(f"  - ID: {et.get('id')}, Title: {et.get('title')}, Length: {et.get('length')} min")
    else:
        logger.error(f"Error retrieving event types: {event_types_result.get('message')}")
        if 'details' in event_types_result:
            logger.error(f"Details: {event_types_result.get('details')}")
    
    logger.info("===== Test Complete =====")

if __name__ == "__main__":
    asyncio.run(test_cal_api_connection()) 