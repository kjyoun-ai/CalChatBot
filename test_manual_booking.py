"""
Manual booking test script using the fixed Cal.com API client.

This script tests the booking API directly with the parameters we know work from our testing.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.api.cal_api import CalAPIClient

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_manual_booking():
    """Test booking directly with known working parameters."""
    logger.info("=== Manual Booking Test ===")
    
    # Create the Cal API client
    cal_api = CalAPIClient()
    
    # Test connection
    connection_success = await cal_api.test_api_connection()
    logger.info(f"API connection successful: {connection_success}")
    
    if not connection_success:
        logger.error("Cannot proceed without API connection")
        return
    
    # 1. First, get event types to verify we have the right ID
    logger.info("\n1. Getting event types...")
    event_types = await cal_api.get_event_types()
    
    if "event_types" in event_types:
        for event_type in event_types["event_types"]:
            logger.info(f"Event Type: {event_type['id']} - {event_type.get('title')} - {event_type.get('slug')}")
    else:
        logger.error(f"Failed to get event types: {event_types}")
    
    # Using the known working event type ID 
    event_type_id = "2457598"
    
    # 2. Check availability for tomorrow at 10:00 PM (known working time from our tests)
    logger.info("\n2. Checking availability...")
    
    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")
    
    # Time that succeeded in our tests (10:00 PM)
    time_str = "22:00"
    iso_datetime = f"{date_str}T{time_str}:00.000Z"
    
    # Check if time is available
    availability_result = await cal_api.get_availability(event_type_id, date_str)
    logger.info(f"Availability data: {availability_result}")
    
    # 3. Attempt booking with the time that worked in our test
    logger.info("\n3. Attempting to book with known parameters...")
    booking_result = await cal_api.book_event(
        event_type_id=event_type_id,
        start_time=iso_datetime,
        name="Test User",
        email="kjyoun3@gmail.com",
        reason="Manual booking test"
    )
    
    logger.info(f"Booking result: {booking_result}")
    
    # 4. Try with time slot checking first
    logger.info("\n4. Checking if time is available before booking...")
    is_available = await cal_api.is_time_available(event_type_id, iso_datetime)
    logger.info(f"Time {iso_datetime} is available: {is_available}")
    
    if is_available:
        logger.info("Time is available, attempting to book...")
        booking_result2 = await cal_api.book_event(
            event_type_id=event_type_id,
            start_time=iso_datetime,
            name="Test User 2",
            email="kjyoun3+test@gmail.com",
            reason="Manual booking test with availability check"
        )
        logger.info(f"Booking result with availability check: {booking_result2}")
    else:
        logger.info("Time is not available, skipping booking attempt")
    
    logger.info("=== Manual Booking Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_manual_booking()) 