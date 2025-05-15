#!/bin/bash
# Test script to directly test the Cal.com API using curl

# Set your API key - this should be filled in from the environment or config
API_KEY="cal_live_3aca2bb2290098e46c06de81fae58cd7"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Cal.com API Direct Testing Script ===${NC}"
echo ""

# Test 1: Check API connection (schedules endpoint)
echo -e "${BLUE}Test 1: Testing API connection${NC}"
connection_result=$(curl -s "https://api.cal.com/v1/schedules?apiKey=$API_KEY" -o /dev/null -w "%{http_code}")

if [ "$connection_result" = "200" ]; then
    echo -e "${GREEN}✅ API connection successful (HTTP 200)${NC}"
else
    echo -e "${RED}❌ API connection failed (HTTP $connection_result)${NC}"
    echo "Exiting script - cannot proceed without API connection"
    exit 1
fi

echo ""

# Test 2: List event types
echo -e "${BLUE}Test 2: Listing event types${NC}"
echo "curl -s \"https://api.cal.com/v1/event-types?apiKey=$API_KEY\""
event_types_response=$(curl -s "https://api.cal.com/v1/event-types?apiKey=$API_KEY")
echo "$event_types_response" | grep -q "\"event_types\":"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully retrieved event types${NC}"
    # Extract event type IDs if needed
    event_type_ids=$(echo "$event_types_response" | grep -o '"id":[0-9]*' | cut -d':' -f2)
    echo "Available event type IDs: $event_type_ids"
else
    echo -e "${RED}❌ Failed to retrieve event types${NC}"
    echo "Response: $event_types_response"
fi

echo ""

# Test 3: Book a meeting with the exact working parameters
echo -e "${BLUE}Test 3: Testing booking with known working parameters${NC}"
echo "curl --request POST \\"
echo "  --url 'https://api.cal.com/v1/bookings?apiKey=$API_KEY' \\"
echo "  --header 'Content-Type: application/json' \\"
echo "  --data '{
  \"eventTypeId\": 2457598,
  \"start\": \"2025-05-27T22:30:00.000Z\",
  \"responses\": {
    \"name\": \"jisoo\",
    \"email\": \"kjyoun3@gmail.com\",
    \"location\": {
      \"optionValue\": \"option\",
      \"value\": \"value\"
    }
  },
  \"timeZone\": \"Asia/Kolkata\",
  \"language\": \"en\",
  \"metadata\": {}
}'"

booking_response=$(curl -s --request POST \
  --url "https://api.cal.com/v1/bookings?apiKey=$API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
  "eventTypeId": 2457598,
  "start": "2025-05-27T22:30:00.000Z",
  "responses": {
    "name": "jisoo",
    "email": "kjyoun3@gmail.com",
    "location": {
      "optionValue": "option",
      "value": "value"
    }
  },
  "timeZone": "Asia/Kolkata",
  "language": "en",
  "metadata": {}
}')

if echo "$booking_response" | grep -q "\"uid\":"; then
    echo -e "${GREEN}✅ Booking successful${NC}"
    booking_id=$(echo "$booking_response" | grep -o '"uid":"[^"]*' | cut -d':' -f2 | tr -d '"')
    echo "Booking ID: $booking_id"
    echo "Full response:"
    echo "$booking_response"
else
    echo -e "${RED}❌ Booking failed${NC}"
    echo "Response: $booking_response"
    
    # Try to identify the error
    if echo "$booking_response" | grep -q "no_available_users_found_error"; then
        echo "Error: No available users found for the specified time"
    elif echo "$booking_response" | grep -q "invalid_number"; then
        echo "Error: Invalid number format in the location field"
    elif echo "$booking_response" | grep -q "database"; then
        echo "Error: Database issue on the server side"
    fi
fi

echo ""

# Test 4: Variation - try different time slots
echo -e "${BLUE}Test 4: Testing booking with different time slot${NC}"
# Get tomorrow's date in YYYY-MM-DD format
tomorrow=$(date -v+1d +%Y-%m-%d)
echo "Using tomorrow's date: $tomorrow"

booking_response2=$(curl -s --request POST \
  --url "https://api.cal.com/v1/bookings?apiKey=$API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
  "eventTypeId": 2457598,
  "start": "'$tomorrow'T14:30:00.000Z",
  "responses": {
    "name": "jisoo",
    "email": "kjyoun3@gmail.com",
    "location": {
      "optionValue": "option",
      "value": "value"
    }
  },
  "timeZone": "Asia/Kolkata",
  "language": "en",
  "metadata": {}
}')

if echo "$booking_response2" | grep -q "\"uid\":"; then
    echo -e "${GREEN}✅ Booking with alternative time successful${NC}"
    booking_id=$(echo "$booking_response2" | grep -o '"uid":"[^"]*' | cut -d':' -f2 | tr -d '"')
    echo "Booking ID: $booking_id"
else
    echo -e "${RED}❌ Booking with alternative time failed${NC}"
    echo "Response: $booking_response2"
fi

echo ""
echo -e "${BLUE}=== Testing complete ===${NC}" 