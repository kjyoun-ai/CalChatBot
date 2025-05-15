"""
Simple test to verify availability.
"""
import os
import sys
import asyncio
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.api.cal_api import CalAPIClient

async def test_simple_availability():
    """Test simple availability check for 2-5pm tomorrow."""
    print("\n=== Testing Simple Availability ===")
    
    # Create the Cal API client
    cal_api = CalAPIClient()
    
    # Get tomorrow's date
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Checking availability for: {tomorrow}")
    
    # Get the 30-minute meeting event type ID (we know this is 2457598)
    event_type_id = "2457598"
    
    # Check availability for tomorrow
    print(f"\nChecking availability for event type {event_type_id} on {tomorrow}...")
    availability_result = await cal_api.get_availability(event_type_id, tomorrow)
    
    if availability_result.get("status") != "success":
        print(f"Error getting availability: {availability_result.get('message', 'Unknown error')}")
        return
    
    # Print availability information
    availability_data = availability_result.get("availability", {})
    date_ranges = availability_data.get("dateRanges", [])
    
    print("\nAvailable time slots from Cal.com API:")
    for date_range in date_ranges:
        start = date_range.get("start")
        end = date_range.get("end")
        print(f"  {start} to {end}")
    
    # Check specific times from 2-5pm
    times_to_check = [
        f"{tomorrow}T14:00:00.000Z",  # 2pm
        f"{tomorrow}T15:00:00.000Z",  # 3pm
        f"{tomorrow}T16:00:00.000Z",  # 4pm
        f"{tomorrow}T17:00:00.000Z",  # 5pm
    ]
    
    print("\nVerifying specific time slots:")
    for time_str in times_to_check:
        # Convert to a more readable format
        time_parts = time_str.split("T")
        hour = int(time_parts[1].split(":")[0])
        hour_pst = (hour - 7) % 24
        am_pm = "AM" if hour_pst < 12 else "PM"
        hour_display = hour_pst % 12
        if hour_display == 0:
            hour_display = 12
            
        print(f"Checking {hour_display}:00 {am_pm} PST ({time_str})...")
        is_available = await cal_api.is_time_available(event_type_id, time_str)
        print(f"  Available: {is_available}")
        
        # Add a brief delay to avoid rate limits
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_simple_availability()) 