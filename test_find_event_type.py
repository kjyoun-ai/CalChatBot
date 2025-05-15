"""
Test script to find the correct event type ID for a 1-hour meeting and check available time slots.
"""
import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
import time

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.api.cal_api import CalAPIClient

async def find_hour_meeting_type():
    """
    Find the correct event type ID for a 1-hour meeting and check available time slots.
    """
    print("\n=== Finding 1-Hour Meeting Event Type ===")
    
    # Create the Cal API client
    cal_api = CalAPIClient()
    
    # Get all event types
    event_types_result = await cal_api.get_event_types()
    
    # Find event types with 60-minute duration
    hour_event_types = []
    print("\nAll Event Types:")
    if isinstance(event_types_result, dict) and "event_types" in event_types_result:
        for event_type in event_types_result["event_types"]:
            print(f"ID: {event_type.get('id')} - {event_type.get('title')} - Duration: {event_type.get('length')} min")
            if "link" in event_type:
                print(f"  Link: {event_type.get('link')}")
            
            # Check if this is a 60-minute meeting
            if event_type.get('length') == 60:
                hour_event_types.append(event_type)
    
    if hour_event_types:
        print("\nFound 1-Hour Meeting Event Types:")
        for event_type in hour_event_types:
            print(f"ID: {event_type.get('id')} - {event_type.get('title')}")
    else:
        print("\nNo 1-hour meeting event types found. Using 30-minute type for testing.")
    
    # Use the first hour event type if found, otherwise use the 30-minute type
    target_event_id = hour_event_types[0].get('id') if hour_event_types else "2457598"
    
    # Get tomorrow's date
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"\nChecking availability for event type {target_event_id} on {tomorrow}")
    
    # Check availability for tomorrow
    availability_result = await cal_api.get_availability(target_event_id, tomorrow)
    
    # Print availability result for debugging
    print("\nRaw Availability Data:")
    print(json.dumps(availability_result, indent=2))
    
    # Check if 2pm PST tomorrow is available
    time_to_check = f"{tomorrow}T14:00:00.000Z"
    print(f"\nSpecifically checking if 2:00 PM PST ({time_to_check}) is available:")
    is_available = await cal_api.is_time_available(target_event_id, time_to_check)
    print(f"2:00 PM PST is available: {is_available}")
    
    # Delay to avoid rate limits
    time.sleep(1)
    
    # Check if 3pm PST tomorrow is available
    time_to_check = f"{tomorrow}T15:00:00.000Z"
    print(f"\nSpecifically checking if 3:00 PM PST ({time_to_check}) is available:")
    is_available = await cal_api.is_time_available(target_event_id, time_to_check)
    print(f"3:00 PM PST is available: {is_available}")
    
    # Delay to avoid rate limits
    time.sleep(1)
    
    # Check if 4pm PST tomorrow is available
    time_to_check = f"{tomorrow}T16:00:00.000Z"
    print(f"\nSpecifically checking if 4:00 PM PST ({time_to_check}) is available:")
    is_available = await cal_api.is_time_available(target_event_id, time_to_check)
    print(f"4:00 PM PST is available: {is_available}")
    
    # Close the API client
    if hasattr(cal_api, 'client') and cal_api.client:
        await cal_api.client.aclose()

if __name__ == "__main__":
    asyncio.run(find_hour_meeting_type()) 