"""
Test script to check actual availability for tomorrow for a 1-hour meeting.
"""
import os
import sys
import asyncio
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.api.cal_api import CalAPIClient

async def test_availability():
    """Test which time slots are actually available for tomorrow."""
    print("\n=== Testing Actual Availability ===")
    
    # Create the Cal API client
    cal_api = CalAPIClient()
    
    # Get tomorrow's date
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Checking availability for: {tomorrow}")
    
    # First, get the event types to find the 1-hour and 30-minute meeting types
    event_types_result = await cal_api.get_event_types()
    print("\nEvent Types:")
    if isinstance(event_types_result, dict) and "event_types" in event_types_result:
        for event_type in event_types_result["event_types"]:
            print(f"ID: {event_type.get('id')} - {event_type.get('title')} - Duration: {event_type.get('length')} min")
            if "link" in event_type:
                print(f"  Link: {event_type.get('link')}")
    
    # Test with the known 1-hour event type ID
    event_type_id = "2457598"  # The ID we've been using
    
    # Check availability for tomorrow
    availability_result = await cal_api.get_availability(event_type_id, tomorrow)
    
    print(f"\nAvailability for event type {event_type_id} on {tomorrow}:")
    print(json.dumps(availability_result, indent=2))
    
    # Extract and print available time slots
    if availability_result.get("status") == "success":
        availability_data = availability_result.get("availability", {})
        date_ranges = availability_data.get("dateRanges", [])
        
        print("\nAvailable time slots:")
        for date_range in date_ranges:
            start = date_range.get("start")
            end = date_range.get("end")
            print(f"  {start} to {end}")
            
            # Also check if specific times within this range are available
            if start and end:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                pst_start = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                pst_end = datetime.fromisoformat(end.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                print(f"  PST: {pst_start} to {pst_end}")
                
                # Check specific times
                for hour in range(14, 18):  # 2pm to 5pm
                    time_str = f"{tomorrow}T{hour:02d}:00:00.000Z"
                    is_available = await cal_api.is_time_available(event_type_id, time_str)
                    print(f"  {hour}:00 PST ({time_str}) available: {is_available}")
    
    # Close the client
    await cal_api.cleanup()

if __name__ == "__main__":
    asyncio.run(test_availability()) 