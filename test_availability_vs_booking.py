#!/usr/bin/env python
"""
Test script to compare the response of checking availability vs booking
to identify why slots appear available but can't be booked
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from src.api.cal_api import CalAPIClient

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_availability_vs_booking():
    """Compare availability check vs actual booking attempt"""
    try:
        # Initialize Cal API client
        cal_api = CalAPIClient()
        
        # Test API connection
        connection_success = await cal_api.test_api_connection()
        print(f"API connection test: {'Success' if connection_success else 'Failed'}")
        
        # Get tomorrow's date for testing
        tomorrow = datetime.now() + timedelta(days=1)
        test_date = tomorrow.strftime("%Y-%m-%d")
        test_time = "14:00:00"  # 2 PM
        test_iso = f"{test_date}T{test_time}.000Z"
        
        print(f"\n===== TESTING SLOT: {test_date} @ {test_time} =====")
        
        # Step 1: Get event type for 30-minute meeting
        print("\n[Step 1] Getting event type for 30-minute meeting")
        event_type_result = await cal_api.get_event_type_by_duration(30)
        
        if event_type_result.get("status") != "success":
            print(f"Error getting event type: {event_type_result.get('message')}")
            return
        
        event_type = event_type_result.get("event_type", {})
        event_type_id = str(event_type.get("id"))
        print(f"Found event type: {event_type.get('title')} (ID: {event_type_id})")
        
        # Step 2: Check availability for the date
        print(f"\n[Step 2] Checking availability for date {test_date}")
        availability_result = await cal_api.get_availability(
            event_type_id=event_type_id, 
            start_date=test_date
        )
        
        if availability_result.get("status") != "success":
            print(f"Error getting availability: {availability_result.get('message')}")
            return
        
        availability_data = availability_result.get("availability", {})
        date_ranges = availability_data.get("dateRanges", [])
        
        print(f"Found {len(date_ranges)} date ranges")
        for i, date_range in enumerate(date_ranges[:3]):  # Show first 3 ranges
            print(f"Range {i+1}: {date_range.get('start')} to {date_range.get('end')}")
        
        # Step 3: Check if our test time is available (API won't give a reliable answer)
        print(f"\n[Step 3] Checking if specific time {test_iso} is available")
        is_available = await cal_api.is_time_available(event_type_id, test_iso)
        print(f"API says time is available: {is_available}")
        
        # Step 4: Attempt to book the slot that should be available
        print(f"\n[Step 4] Attempting to book the slot")
        booking_result = await cal_api.book_event(
            event_type_id=event_type_id,
            start_time=test_iso,
            name="Test User",
            email="test@example.com",
            reason="Testing availability vs booking"
        )
        
        # Step 5: Analyze the results
        print("\n===== ANALYSIS =====")
        print(f"Availability Check: {'PASS' if is_available else 'FAIL'}")
        print(f"Booking Attempt: {'PASS' if booking_result.get('status') != 'error' else 'FAIL'}")
        
        if booking_result.get("status") == "error":
            error_message = booking_result.get("message", "Unknown error")
            print(f"Booking Error: {error_message}")
            
            # Look for specific error messages
            if "no_available_users_found_error" in error_message:
                print("\nROOT CAUSE IDENTIFIED: 'no_available_users_found_error'")
                print("This typically means the host has conflicts in their schedule that aren't reflected in")
                print("the availability API response. The Cal.com API returns general time slots as 'available'")
                print("but then rejects bookings when there are conflicts with specific users.")
            
            if "Invalid event length" in error_message:
                print("\nROOT CAUSE IDENTIFIED: 'Invalid event length'")
                print("This typically means the calculated end time does not work with the event type's")
                print("required duration. Check duration calculation and the event type settings.")
    
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_availability_vs_booking()

if __name__ == "__main__":
    asyncio.run(main()) 