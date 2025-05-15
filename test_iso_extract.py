#!/usr/bin/env python
"""
Test the ISO datetime extraction function.
"""

import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("iso_test")

def extract_iso_datetime(message: str):
    """
    Extract ISO 8601 datetime from a message.
    """
    # Pattern to match ISO 8601 datetime (e.g., 2025-05-14T20:30:00.000Z)
    iso_pattern = r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}):00\.000Z'
    match = re.search(iso_pattern, message)
    
    if match:
        date_str = match.group(1)  # YYYY-MM-DD
        time_str = match.group(2)  # HH:MM
        
        logger.info(f"Extracted ISO date: {date_str}, time: {time_str} from message")
        return {
            "date": date_str,
            "time": time_str
        }
    return {}

def main():
    """Test various ISO datetime formats."""
    test_messages = [
        "book a 30 min meeting for 2025-05-14T20:30:00.000Z",
        "I need to schedule something on 2023-12-25T14:15:00.000Z for a Christmas meeting",
        "No date here",
        "Partial date: 2025-05-14"
    ]
    
    for message in test_messages:
        logger.info(f"Testing message: {message}")
        result = extract_iso_datetime(message)
        logger.info(f"Result: {result}")
        print("-" * 50)

if __name__ == "__main__":
    main() 