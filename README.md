# Cal Scheduler Agent

A smart AI-powered chatbot that helps schedule meetings through the Cal.com API. The agent uses natural language processing to understand user intent and can book meetings, check availability, list events, and more.

## Features

- **Natural Language Scheduling**: Schedule meetings by chatting in natural language
- **Timezone-Aware**: Handles timezone conversions automatically (defaults to PST)
- **Availability Checking**: View available time slots for specific dates
- **Meeting Management**: Book, list, and cancel meetings
- **Contextual Understanding**: Maintains conversation context for seamless interactions

## Installation

### Prerequisites

- Python 3.9+
- Cal.com API key
- OpenAI API key

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd CalSchedulerAgent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   
   Create a `.env` file in the project root with the following variables:
   ```
   CAL_API_KEY=your_cal_api_key
   CAL_API_URL=https://api.cal.com/v1
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-3.5-turbo
   LOG_LEVEL=INFO
   ```

## Usage

### Starting the API Server

To start the API server:

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

This will start a FastAPI server on http://localhost:8000

```bash
streamlit run app.py
```
This will start a frontend server on http://localhost:8501/

### Chatting with the Agent

You can interact with the agent using the following endpoints:

- **Start a conversation**:
  `POST /conversation` - Creates a new conversation and returns a conversation ID

- **Send a message**:
  `POST /chat` - Send a message to the agent
  ```json
  {
    "message": "I'd like to book a meeting on May 20th at 2pm",
    "conversation_id": "your_conversation_id"
  }
  ```

- **Check conversation status**:
  `GET /conversation/{conversation_id}` - Get the status of a conversation

### Example Usage

The agent can handle various scheduling requests:

- "I'd like to book a 30-minute meeting on May 20th at 2pm"
- "What times are available tomorrow?"
- "Can you list my upcoming meetings?"
- "I need to cancel my meeting on Thursday"
- "Reschedule my meeting to Friday at 3pm"
- "When's the earliest slot you have tomorrow?"

## Key Components

- **Chatbot**: Core chat logic handling user conversations
- **OpenAI Integration**: Recognizes user intent and extracts booking parameters
- **Cal API Client**: Integrates with Cal.com for scheduling functions
- **FastAPI Server**: Exposes the agent through REST endpoints

## Timezone Handling

The agent assumes times are in Pacific Time (PST/PDT) by default. When specifying times, you can include timezone indicators:

- "Book a meeting at 2:00 PM PST"
- "Book a meeting at 5:00 PM EST"

If no timezone is specified, the system assumes PST.

## Development

### Project Structure

- `/src/api`: Cal.com API integration
- `/src/bot`: Chatbot and OpenAI integration
- `/src/utils`: Configuration and utility functions

### Logging

Logs are output to the console with the level specified in the `.env` file. For more detailed logs, set `LOG_LEVEL=DEBUG`.

## Troubleshooting

- **Authentication Errors**: Check your Cal.com and OpenAI API keys
- **Booking Errors**: Ensure the requested time is within available hours (typically 9AM-5PM PST)
- **Timezone Issues**: Be explicit about timezones when booking meetings

## License

[Specify your license here] 