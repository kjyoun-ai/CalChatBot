"""
Main application entry point for the Cal.com Scheduler Agent.
"""

import os
import uuid
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header, Query, Path, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, EmailStr

from src.bot.chatbot import CalendarAgent
from src.utils.config import validate_config, logger, get_api_key
from src.api.cal_api import CalAPIClient

# Load environment variables
load_dotenv()

# Validate configuration
if not validate_config():
    logger.warning("Missing required environment variables. Some features may not work correctly.")

# Initialize FastAPI app
app = FastAPI(
    title="Cal.com Scheduler Agent API",
    description="""
    A REST API for interacting with the Cal.com Scheduler Agent chatbot.
    
    This API allows you to:
    * Send messages to the chatbot and get responses
    * Manage conversations
    * Check calendar availability
    * Book, cancel, and reschedule meetings
    
    All endpoints require API key authentication.
    """,
    version="0.1.0",
    docs_url=None,
    redoc_url="/api/docs",
    openapi_url="/api/openapi.json",
    contact={
        "name": "Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# In-memory storage for conversations (replace with database in production)
conversations = {}

# Models
class ChatMessage(BaseModel):
    """User message model."""
    message: str = Field(..., description="The message content to send to the chatbot", example="Can you book a meeting for me on Monday at 2pm?")
    user_email: EmailStr = Field(..., description="The email of the user sending the message", example="user@example.com")
    conversation_id: Optional[str] = Field(None, description="Optional ID of an existing conversation", example="550e8400-e29b-41d4-a716-446655440000")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Book a meeting for tomorrow at 3pm",
                "user_email": "user@example.com",
                "conversation_id": None
            }
        }

class Message(BaseModel):
    """Message model for conversation history."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the message")
    content: str = Field(..., description="Content of the message")
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Timestamp when the message was created")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "content": "Book a meeting for tomorrow at 3pm",
                "role": "user",
                "created_at": "2023-03-01T14:00:00.000Z"
            }
        }

class Conversation(BaseModel):
    """Conversation model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the conversation")
    user_email: EmailStr = Field(..., description="Email of the user owning the conversation")
    messages: List[Message] = Field(default_factory=list, description="List of messages in the conversation")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Timestamp when the conversation was created")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Timestamp when the conversation was last updated")

class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str = Field(..., description="The chatbot's response message")
    conversation_id: str = Field(..., description="The ID of the conversation")
    action_taken: Optional[str] = Field(None, description="Action taken by the chatbot, if any")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details about the action taken")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "I've booked a meeting for you tomorrow at 3pm. You'll receive an email confirmation shortly.",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "action_taken": "book_meeting",
                "details": {
                    "meeting_id": "123456",
                    "start_time": "2023-03-02T15:00:00.000Z",
                    "end_time": "2023-03-02T16:00:00.000Z"
                }
            }
        }

class NewConversation(BaseModel):
    """Model for creating a new conversation."""
    user_email: EmailStr = Field(..., description="Email of the user creating the conversation", example="user@example.com")
    
    class Config:
        schema_extra = {
            "example": {
                "user_email": "user@example.com"
            }
        }

class AvailabilityRequest(BaseModel):
    """Model for requesting available slots."""
    event_type_id: str = Field(..., description="ID of the event type to check availability for", example="1")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format", example="2023-03-01")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format", example="2023-03-07")
    
    class Config:
        schema_extra = {
            "example": {
                "event_type_id": "1",
                "start_date": "2023-03-01",
                "end_date": "2023-03-07"
            }
        }

class BookEventRequest(BaseModel):
    """Model for booking a new event."""
    event_type_id: str = Field(default="1", description="ID of the event type to book", example="1")
    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2023-03-02")
    time: str = Field(..., description="Time in HH:MM format", example="15:00")
    name: str = Field(..., description="Name of the attendee", example="John Doe")
    email: EmailStr = Field(..., description="Email of the attendee", example="user@example.com")
    reason: Optional[str] = Field(None, description="Reason for the meeting", example="Discuss project requirements")
    
    class Config:
        schema_extra = {
            "example": {
                "event_type_id": "1",
                "date": "2023-03-02",
                "time": "15:00",
                "name": "John Doe",
                "email": "user@example.com",
                "reason": "Discuss project requirements"
            }
        }

class RescheduleEventRequest(BaseModel):
    """Model for rescheduling an event."""
    new_date: str = Field(..., description="New date in YYYY-MM-DD format", example="2023-03-03")
    new_time: str = Field(..., description="New time in HH:MM format", example="14:00")
    
    class Config:
        schema_extra = {
            "example": {
                "new_date": "2023-03-03",
                "new_time": "14:00"
            }
        }

# Helper functions
def verify_api_key(api_key: str = Header(None, alias=API_KEY_NAME)):
    """Verify the API key."""
    # In production, use a more secure approach for storing and validating API keys
    valid_api_key = os.getenv("API_KEY", "test-api-key")
    if api_key != valid_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# Create a dependency to get the chatbot agent
# Single shared instance for all requests
_agent_instance = None

def get_agent():
    """Get or create a CalendarAgent instance as a singleton to maintain context."""
    global _agent_instance
    if _agent_instance is None:
        try:
            _agent_instance = CalendarAgent()
            logger.info("Created singleton CalendarAgent instance")
        except Exception as e:
            logger.error(f"Failed to initialize CalendarAgent: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize chatbot")
    return _agent_instance

# Create a dependency to get the Cal.com API client
async def get_cal_api():
    """Get or create a CalAPIClient instance."""
    try:
        client = CalAPIClient()
        yield client
    except Exception as e:
        logger.error(f"Failed to initialize CalAPIClient: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize Cal.com API client")

# Custom Swagger UI route
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve custom Swagger UI."""
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="Cal.com Scheduler Agent API",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/", tags=["General"])
async def root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to Cal.com Scheduler Agent API", "documentation": "/api/docs"}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    message: ChatMessage, 
    agent: CalendarAgent = Depends(get_agent),
    api_key: str = Depends(verify_api_key)
):
    """
    Send a message to the chatbot and get a response.
    
    This endpoint processes user messages through the chatbot agent and returns:
    - The chatbot's response
    - The conversation ID (new or existing)
    - Any action taken by the chatbot
    - Details about the action
    
    If you don't provide a conversation_id, a new conversation will be created.
    """
    try:
        # Get or create conversation
        conversation_id = message.conversation_id
        if not conversation_id or conversation_id not in conversations:
            # Create new conversation
            conversation = Conversation(user_email=message.user_email)
            conversation_id = conversation.id
            conversations[conversation_id] = conversation
            logger.info(f"Created new conversation: {conversation_id}")
        else:
            # Get existing conversation
            conversation = conversations[conversation_id]
            # Update conversation
            conversation.updated_at = datetime.now(timezone.utc).isoformat()
            
        # Add user message to conversation
        user_message = Message(
            content=message.message,
            role="user"
        )
        conversation.messages.append(user_message)
        
        # Process the message with our agent
        result = await agent.process_message(
            message=message.message,
            user_email=message.user_email
        )
        
        # Add assistant message to conversation
        assistant_message = Message(
            content=result["response"],
            role="assistant"
        )
        conversation.messages.append(assistant_message)
        
        # Update the conversation in our storage
        conversations[conversation_id] = conversation
        
        return ChatResponse(
            response=result["response"],
            conversation_id=conversation_id,
            action_taken=result["action_taken"],
            details=result["details"]
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Conversation Management Endpoints
@app.get("/api/conversations", response_model=List[Dict[str, Any]], tags=["Conversations"])
async def list_conversations(
    user_email: Optional[str] = Query(None, description="Filter conversations by user email"),
    api_key: str = Depends(verify_api_key)
):
    """
    List all conversations, optionally filtered by user_email.
    
    Returns a list of conversation summaries including:
    - Conversation ID
    - User email
    - Creation and update timestamps
    - Message count
    """
    try:
        result = []
        for conv_id, conversation in conversations.items():
            if user_email is None or conversation.user_email == user_email:
                result.append({
                    "id": conversation.id,
                    "user_email": conversation.user_email,
                    "created_at": conversation.created_at,
                    "updated_at": conversation.updated_at,
                    "message_count": len(conversation.messages)
                })
        return result
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations", status_code=status.HTTP_201_CREATED, tags=["Conversations"])
async def create_conversation(
    conversation: NewConversation,
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new conversation.
    
    Returns:
    - The new conversation ID
    - User email
    - Creation timestamp
    - Message count (initially 0)
    """
    try:
        new_conversation = Conversation(user_email=conversation.user_email)
        conversations[new_conversation.id] = new_conversation
        logger.info(f"Created new conversation: {new_conversation.id}")
        return {
            "id": new_conversation.id,
            "user_email": new_conversation.user_email,
            "created_at": new_conversation.created_at,
            "message_count": 0
        }
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}", tags=["Conversations"])
async def get_conversation(
    conversation_id: str = Path(..., description="The ID of the conversation to retrieve"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get details of a specific conversation by ID.
    
    Returns:
    - Conversation ID
    - User email
    - Creation and update timestamps
    - Message count
    
    Raises a 404 error if the conversation is not found.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations[conversation_id]
    return {
        "id": conversation.id,
        "user_email": conversation.user_email,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "message_count": len(conversation.messages)
    }

@app.delete("/api/conversations/{conversation_id}", tags=["Conversations"])
async def delete_conversation(
    conversation_id: str = Path(..., description="The ID of the conversation to delete"),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a specific conversation by ID.
    
    Returns a confirmation message upon successful deletion.
    
    Raises a 404 error if the conversation is not found.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    del conversations[conversation_id]
    return {"message": f"Conversation {conversation_id} deleted"}

@app.get("/api/conversations/{conversation_id}/messages", tags=["Conversations"])
async def get_conversation_messages(
    conversation_id: str = Path(..., description="The ID of the conversation"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all messages for a specific conversation.
    
    Returns a list of message objects, each containing:
    - Message ID
    - Content
    - Role (user or assistant)
    - Creation timestamp
    
    Raises a 404 error if the conversation is not found.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations[conversation_id]
    return conversation.messages

# Calendar API Endpoints
@app.get("/api/calendar/availability", tags=["Calendar"])
async def get_availability(
    event_type_id: str = Query(..., description="The event type ID"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    cal_api: CalAPIClient = Depends(get_cal_api),
    api_key: str = Depends(verify_api_key)
):
    """
    Get available time slots for a specific event type.
    
    Returns a list of available time slots between the specified dates.
    
    Each slot includes:
    - Start time
    - End time
    - Availability status
    """
    print("event_type_id:", event_type_id)
    print("start_date:", start_date)
    print("end_date:", end_date)
    try:
        slots = await cal_api.get_available_slots(event_type_id, start_date, end_date)
        return slots
    except Exception as e:
        logger.error(f"Error getting available slots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calendar/events", status_code=status.HTTP_201_CREATED, tags=["Calendar"])
async def book_event(
    event: BookEventRequest,
    cal_api: CalAPIClient = Depends(get_cal_api),
    api_key: str = Depends(verify_api_key)
):
    """
    Book a new event on the calendar.
    
    Returns details of the booked event, including:
    - Event ID
    - Start and end time
    - Attendee information
    - Any additional details from Cal.com
    
    Raises a 400 error if booking fails.
    """
    try:
        # Format the date and time as ISO string (YYYY-MM-DDThh:mm:00.000Z)
        start_time = f"{event.date}T{event.time}:00.000Z"
        
        # Call the Cal.com API to book the meeting
        booking_result = await cal_api.book_event(
            event_type_id=event.event_type_id,
            start_time=start_time,
            name=event.name,
            email=event.email,
            reason=event.reason
        )
        
        if booking_result.get("status") == "error":
            error_message = booking_result.get("message", "Failed to book event")
            status_code = status.HTTP_400_BAD_REQUEST
            
            # Handle different error types with appropriate status codes
            if "500" in error_message and "database" in error_message.lower():
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
                error_detail = "Calendar service is temporarily unavailable. Please try again later."
            elif "404" in error_message:
                status_code = status.HTTP_404_NOT_FOUND
                error_detail = "The requested event type could not be found."
            elif "401" in error_message or "403" in error_message:
                status_code = status.HTTP_401_UNAUTHORIZED
                error_detail = "Authentication error with calendar service."
            elif "Invalid time slot" in error_message:
                status_code = status.HTTP_400_BAD_REQUEST
                error_detail = "The requested time slot is not available."
            else:
                error_detail = error_message
                
            raise HTTPException(status_code=status_code, detail=error_detail)
        
        return booking_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error booking event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar/events", tags=["Calendar"])
async def list_events(
    user_email: EmailStr = Query(..., description="Email of the user to list events for"),
    cal_api: CalAPIClient = Depends(get_cal_api),
    api_key: str = Depends(verify_api_key)
):
    """
    List all events for a user.
    
    Returns a list of events, each containing:
    - Event ID
    - Title
    - Start and end time
    - Attendees
    - Status
    """
    try:
        events = await cal_api.list_bookings(user_email)
        return events
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/calendar/events/{event_id}", tags=["Calendar"])
async def cancel_event(
    event_id: str = Path(..., description="The ID of the event to cancel"),
    cal_api: CalAPIClient = Depends(get_cal_api),
    api_key: str = Depends(verify_api_key)
):
    """
    Cancel a specific event by ID.
    
    Returns a confirmation of the cancellation.
    
    Raises a 400 error if cancellation fails.
    """
    try:
        result = await cal_api.cancel_booking(event_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to cancel event"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/calendar/events/{event_id}", tags=["Calendar"])
async def reschedule_event(
    event_id: str = Path(..., description="The ID of the event to reschedule"),
    reschedule_data: RescheduleEventRequest = ...,
    cal_api: CalAPIClient = Depends(get_cal_api),
    api_key: str = Depends(verify_api_key)
):
    """
    Reschedule a specific event by ID.
    
    Returns details of the rescheduled event.
    
    Raises a 400 error if rescheduling fails.
    """
    try:
        # Format the new date and time as ISO string
        new_start_time = f"{reschedule_data.new_date}T{reschedule_data.new_time}:00.000Z"
        
        result = await cal_api.reschedule_booking(event_id, new_start_time)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to reschedule event"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rescheduling event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("src.app:app", host=host, port=port, reload=True) 