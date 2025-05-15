#!/bin/bash
# Test script to check available slots for the Cal.com API

# Set your API key
API_KEY="cal_live_3aca2bb2290098e46c06de81fae58cd7"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Cal.com API Available Slots Check ===${NC}"
echo ""

# Get today's date and future date (7 days from now) in YYYY-MM-DD format
today=$(date +%Y-%m-%d)
future_date=$(date -v+7d +%Y-%m-%d)

# Tomorrow's date for testing
tomorrow=$(date -v+1d +%Y-%m-%d)
echo "Date for testing: $tomorrow"

# First, get event type details to find the username
echo -e "${BLUE}Getting event type details for ID 2457598${NC}"
event_type_response=$(curl -s "https://api.cal.com/v1/event-types/2457598?apiKey=$API_KEY")
echo "$event_type_response" | grep -q "\"link\":"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully retrieved event type details${NC}"
    # Extract username from the link field - format is "https://cal.com/username/slug"
    link=$(echo "$event_type_response" | grep -o '"link":"[^"]*' | head -1 | cut -d':' -f2,3 | tr -d '"')
    echo "Event link: $link"
    
    # Extract username from link
    username=$(echo "$link" | sed -E 's|https://cal.com/([^/]+)/.*|\1|')
    echo "Event owner username: $username"
else
    echo -e "${RED}❌ Failed to retrieve event type details${NC}"
    echo "Response: $event_type_response"
    
    # Fallback to using a username we found from the previous test
    username="jisoo-yun"
    echo "Using fallback username: $username"
fi

# Check available slots for event type 2457598
echo -e "${BLUE}Checking availability for event type 2457598${NC}"
echo "Time range: $today to $future_date"
echo "curl -s \"https://api.cal.com/v1/availability?apiKey=$API_KEY&eventTypeId=2457598&dateFrom=$today&dateTo=$future_date&username=$username\""

availability_response=$(curl -s "https://api.cal.com/v1/availability?apiKey=$API_KEY&eventTypeId=2457598&dateFrom=$today&dateTo=$future_date&username=$username")

# Check if the response contains dateRanges (this format doesn't have "slots" directly)
if echo "$availability_response" | grep -q "\"dateRanges\":"; then
    echo -e "${GREEN}✅ Successfully retrieved availability information${NC}"
    timezone=$(echo "$availability_response" | grep -o '"timeZone":"[^"]*' | head -1 | cut -d':' -f2 | tr -d '"')
    echo "Timezone: $timezone"
    
    # Count the number of available date ranges
    dateranges_count=$(echo "$availability_response" | grep -o '"dateRanges":\[\{' | wc -l)
    echo "Number of dateRanges: $dateranges_count"
    
    # Print the first few date ranges
    echo "First few available date ranges:"
    echo "$availability_response" | grep -o '"start":"[^"]*","end":"[^"]*' | head -5 | while read range; do
        start=$(echo "$range" | grep -o '"start":"[^"]*' | cut -d':' -f2,3,4 | tr -d '"')
        end=$(echo "$range" | grep -o '"end":"[^"]*' | cut -d':' -f2,3,4 | tr -d '"')
        echo "  - $start to $end"
    done
    
    # Use a time from tomorrow in one of the date ranges (simulated slot)
    # Format: YYYY-MM-DDT20:30:00.000Z (assuming evening slot)
    test_time="${tomorrow}T20:30:00.000Z"
    echo ""
    echo -e "${BLUE}Testing booking with time: $test_time${NC}"
    
    booking_response=$(curl -s --request POST \
      --url "https://api.cal.com/v1/bookings?apiKey=$API_KEY" \
      --header 'Content-Type: application/json' \
      --data '{
      "eventTypeId": 2457598,
      "start": "'$test_time'",
      "responses": {
        "name": "jisoo",
        "email": "kjyoun3@gmail.com",
        "location": {
          "optionValue": "option",
          "value": "value"
        }
      },
      "timeZone": "America/Los_Angeles",
      "language": "en",
      "metadata": {}
    }')
    
    if echo "$booking_response" | grep -q "\"uid\":"; then
        echo -e "${GREEN}✅ Booking successful${NC}"
        booking_id=$(echo "$booking_response" | grep -o '"uid":"[^"]*' | cut -d':' -f2 | tr -d '"')
        echo "Booking ID: $booking_id"
        echo "Full response:"
        echo "$booking_response" | python -m json.tool
    else
        echo -e "${RED}❌ Booking failed${NC}"
        echo "Response: $booking_response"
        
        # Trying another slot
        if echo "$booking_response" | grep -q "no_available_users_found_error"; then
            echo ""
            echo -e "${BLUE}Trying with a different time tomorrow afternoon${NC}"
            test_time="${tomorrow}T22:00:00.000Z"
            echo "New test time: $test_time"
            
            booking_response=$(curl -s --request POST \
              --url "https://api.cal.com/v1/bookings?apiKey=$API_KEY" \
              --header 'Content-Type: application/json' \
              --data '{
              "eventTypeId": 2457598,
              "start": "'$test_time'",
              "responses": {
                "name": "jisoo",
                "email": "kjyoun3@gmail.com",
                "location": {
                  "optionValue": "option",
                  "value": "value"
                }
              },
              "timeZone": "America/Los_Angeles",
              "language": "en",
              "metadata": {}
            }')
            
            if echo "$booking_response" | grep -q "\"uid\":"; then
                echo -e "${GREEN}✅ Second booking attempt successful${NC}"
                booking_id=$(echo "$booking_response" | grep -o '"uid":"[^"]*' | cut -d':' -f2 | tr -d '"')
                echo "Booking ID: $booking_id"
                echo "Full response:"
                echo "$booking_response" | python -m json.tool
            else
                echo -e "${RED}❌ Second booking attempt failed${NC}"
                echo "Response: $booking_response"
            fi
        fi
    fi
else
    echo -e "${RED}❌ Failed to retrieve availability information${NC}"
    echo "Response: $availability_response"
fi

echo ""
echo -e "${BLUE}=== Checking complete ===${NC}" 