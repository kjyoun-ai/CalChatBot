#!/usr/bin/env python
"""
Debug test for booking functionality.
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from src.bot.chatbot import CalendarAgent
from src.bot.openai_integration import OpenAIFunctionCaller
from src.api.cal_api import CalAPIClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("booking_test")

async def test_event_types():
    """Test getting event types from the API"""
    client = CalAPIClient()
    logger.info("Getting available event types...")
    event_types = await client.check_available_event_types()
    
    if event_types.get("status") == "success":
        logger.info(f"Found {len(event_types.get('event_types', []))} event types:")
        for et in event_types.get("event_types", []):
            logger.info(f"  - ID: {et.get('id')}, Name: {et.get('title')}, Duration: {et.get('length')} minutes")
        
        # Return the first event type ID we find
        if event_types.get("event_types"):
            return event_types.get("event_types")[0].get("id")
    else:
        logger.error(f"Failed to get event types: {event_types.get('message')}")
    
    return None

async def check_availability(event_type_id):
    """Test checking availability for different dates"""
    client = CalAPIClient()
    logger.info(f"Checking availability for event type {event_type_id}")
    
    # Try multiple dates (today plus 1-7 days)
    today = datetime.now()
    
    for days_ahead in range(1, 8):
        test_date = today + timedelta(days=days_ahead)
        date_str = test_date.strftime("%Y-%m-%d")
        
        logger.info(f"Checking availability for {date_str}")
        availability = await client.get_availability(event_type_id, date_str)
        
        if availability.get("status") == "success":
            avail_data = availability.get("availability", {})
            date_ranges = avail_data.get("dateRanges", [])
            
            if date_ranges:
                logger.info(f"Found {len(date_ranges)} available ranges for {date_str}")
                # Return the first start time we find
                start_time = date_ranges[0].get("start")
                if start_time:
                    logger.info(f"Found available start time: {start_time}")
                    return start_time
            else:
                logger.info(f"No availability found for {date_str}")
        else:
            logger.error(f"Error checking availability: {availability.get('message')}")
    
    return None

async def test_booking_with_found_slot(event_type_id, start_time):
    """Test booking with a time slot we found available"""
    client = CalAPIClient()
    logger.info(f"Testing booking with found slot: {start_time}")
    
    result = await client.book_event(
        event_type_id=str(event_type_id),
        start_time=start_time,
        name='Test User',
        email='test@example.com',
        reason='Testing booking with available slot'
    )
    
    if result.get("status") == "error":
        logger.error(f"Booking error: {result.get('message')}")
    else:
        logger.info(f"Booking successful! Booking ID: {result.get('uid', 'unknown')}")
    
    return result

async def main():
    """Main test function"""
    logger.info("Starting Cal.com API tests")
    
    # First, get available event types
    event_type_id = await test_event_types()
    if not event_type_id:
        logger.error("Could not find any event types, aborting test")
        return
    
    # Force the use of 30 Min Meeting event type
    event_type_id = 2477342
    logger.info(f"Using event type ID: {event_type_id}")
    
    # Then check availability to find an open slot
    available_time = await check_availability(event_type_id)
    if not available_time:
        logger.error("Could not find any available time slots, aborting test")
        return
    
    logger.info(f"Found available time slot: {available_time}")
    
    # Finally, try to book the available slot
    booking_result = await test_booking_with_found_slot(event_type_id, available_time)
    logger.info("Test completed")

if __name__ == "__main__":
    asyncio.run(main()) 