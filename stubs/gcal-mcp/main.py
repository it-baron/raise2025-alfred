#!/usr/bin/env python3
"""
Google Calendar MCP Stub Server
Provides stubbed Google Calendar API responses for Phase 0 testing
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Google Calendar MCP Stub Server",
    description="Stubbed Google Calendar API responses for Alfred Phase 0",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class MCPRequest(BaseModel):
    task: str
    parameters: Optional[Dict[str, Any]] = {}

class MCPResponse(BaseModel):
    success: bool
    result: Any
    message: str
    timestamp: str

# Stub Data
SAMPLE_EVENTS = [
    {
        "id": "event_001",
        "summary": "Team Standup",
        "description": "Daily team synchronization meeting",
        "start": {
            "dateTime": "2025-01-06T09:00:00Z",
            "timeZone": "Europe/Paris"
        },
        "end": {
            "dateTime": "2025-01-06T09:30:00Z",
            "timeZone": "Europe/Paris"
        },
        "attendees": [
            {"email": "alice@company.com", "responseStatus": "accepted"},
            {"email": "bob@company.com", "responseStatus": "accepted"}
        ],
        "location": "Conference Room A",
        "status": "confirmed",
        "created": "2025-01-05T10:00:00Z"
    },
    {
        "id": "event_002",
        "summary": "Client Presentation",
        "description": "Quarterly review presentation for key client",
        "start": {
            "dateTime": "2025-01-06T14:00:00Z",
            "timeZone": "Europe/Paris"
        },
        "end": {
            "dateTime": "2025-01-06T15:30:00Z",
            "timeZone": "Europe/Paris"
        },
        "attendees": [
            {"email": "client@customer.com", "responseStatus": "needsAction"},
            {"email": "manager@company.com", "responseStatus": "accepted"}
        ],
        "location": "Zoom Meeting",
        "status": "confirmed",
        "created": "2025-01-04T16:00:00Z"
    },
    {
        "id": "event_003",
        "summary": "Lunch with Sarah",
        "description": "Catch up over lunch",
        "start": {
            "dateTime": "2025-01-06T12:00:00Z",
            "timeZone": "Europe/Paris"
        },
        "end": {
            "dateTime": "2025-01-06T13:00:00Z",
            "timeZone": "Europe/Paris"
        },
        "attendees": [
            {"email": "sarah@friend.com", "responseStatus": "accepted"}
        ],
        "location": "Downtown Bistro",
        "status": "confirmed",
        "created": "2025-01-03T18:00:00Z"
    }
]

MEETING_TEMPLATES = {
    "one_on_one": {
        "summary": "1:1 with {person}",
        "description": "Regular one-on-one meeting to discuss progress and goals",
        "duration": 30
    },
    "team_meeting": {
        "summary": "Team Meeting - {topic}",
        "description": "Team discussion about {topic}",
        "duration": 60
    },
    "client_call": {
        "summary": "Client Call - {client}",
        "description": "Call with {client} to discuss {topic}",
        "duration": 45
    },
    "interview": {
        "summary": "Interview - {candidate}",
        "description": "Technical interview with {candidate}",
        "duration": 60
    }
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Google Calendar MCP Stub", "timestamp": datetime.now().isoformat()}

@app.post("/invoke", response_model=MCPResponse)
async def invoke_mcp(request: MCPRequest):
    """Main MCP invocation endpoint"""

    try:
        result = None
        message = "Operation completed successfully"

        if request.task == "list_events":
            result = await list_events(request.parameters)

        elif request.task == "create_event":
            result = await create_event(request.parameters)

        elif request.task == "update_event":
            result = await update_event(request.parameters)

        elif request.task == "delete_event":
            result = await delete_event(request.parameters)

        elif request.task == "find_free_time":
            result = await find_free_time(request.parameters)

        elif request.task == "get_busy_times":
            result = await get_busy_times(request.parameters)

        elif request.task == "quick_add":
            result = await quick_add_event(request.parameters)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown task: {request.task}")

        return MCPResponse(
            success=True,
            result=result,
            message=message,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        return MCPResponse(
            success=False,
            result=None,
            message=f"Error executing task {request.task}: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

async def list_events(params: Dict[str, Any]) -> Dict[str, Any]:
    """List calendar events"""

    time_min = params.get("time_min", datetime.now().isoformat())
    time_max = params.get("time_max", (datetime.now() + timedelta(days=7)).isoformat())
    max_results = params.get("max_results", 10)

    # Filter events by time range
    events = []
    for event in SAMPLE_EVENTS:
        event_start = event["start"]["dateTime"]
        if time_min <= event_start <= time_max:
            events.append(event)

    # Sort by start time
    events.sort(key=lambda x: x["start"]["dateTime"])

    return {
        "events": events[:max_results],
        "total_count": len(events),
        "time_range": {
            "start": time_min,
            "end": time_max
        }
    }

async def create_event(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new calendar event"""

    summary = params.get("summary", "New Event")
    description = params.get("description", "")
    start_time = params.get("start_time")
    end_time = params.get("end_time")
    duration = params.get("duration", 60)  # minutes
    attendees = params.get("attendees", [])
    location = params.get("location", "")
    template = params.get("template", "team_meeting")
    context = params.get("context", {})

    # Use template if provided
    if template in MEETING_TEMPLATES and context:
        template_data = MEETING_TEMPLATES[template]
        if not summary or summary == "New Event":
            summary = template_data["summary"].format(**context)
        if not description:
            description = template_data["description"].format(**context)
        if not end_time and not duration:
            duration = template_data["duration"]

    # Calculate end time if not provided
    if start_time and not end_time:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=duration)
        end_time = end_dt.isoformat()

    event_id = f"event_{random.randint(1000, 9999)}"

    event = {
        "id": event_id,
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time,
            "timeZone": "Europe/Paris"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Europe/Paris"
        },
        "attendees": [{"email": email, "responseStatus": "needsAction"} for email in attendees],
        "location": location,
        "status": "confirmed",
        "created": datetime.now().isoformat()
    }

    return {
        "event": event,
        "message": f"Event '{summary}' created successfully"
    }

async def update_event(params: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing event"""

    event_id = params.get("event_id")
    updates = params.get("updates", {})

    # Find the event (simulated)
    event = None
    for e in SAMPLE_EVENTS:
        if e["id"] == event_id:
            event = e.copy()
            break

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    # Apply updates
    event.update(updates)
    event["updated"] = datetime.now().isoformat()

    return {
        "event": event,
        "message": f"Event {event_id} updated successfully"
    }

async def delete_event(params: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a calendar event"""

    event_id = params.get("event_id")

    return {
        "event_id": event_id,
        "status": "deleted",
        "message": f"Event {event_id} deleted successfully"
    }

async def find_free_time(params: Dict[str, Any]) -> Dict[str, Any]:
    """Find free time slots"""

    date = params.get("date", datetime.now().strftime("%Y-%m-%d"))
    duration = params.get("duration", 60)  # minutes
    working_hours = params.get("working_hours", {"start": "09:00", "end": "17:00"})

    # Generate some free slots (simplified)
    free_slots = [
        {
            "start": f"{date}T10:00:00Z",
            "end": f"{date}T11:00:00Z",
            "duration": 60
        },
        {
            "start": f"{date}T15:00:00Z",
            "end": f"{date}T16:30:00Z",
            "duration": 90
        }
    ]

    return {
        "free_slots": free_slots,
        "date": date,
        "requested_duration": duration,
        "working_hours": working_hours
    }

async def get_busy_times(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get busy time periods"""

    date = params.get("date", datetime.now().strftime("%Y-%m-%d"))

    # Extract busy times from sample events
    busy_times = []
    for event in SAMPLE_EVENTS:
        event_date = event["start"]["dateTime"][:10]
        if event_date == date:
            busy_times.append({
                "start": event["start"]["dateTime"],
                "end": event["end"]["dateTime"],
                "summary": event["summary"]
            })

    return {
        "busy_times": busy_times,
        "date": date,
        "total_busy_periods": len(busy_times)
    }

async def quick_add_event(params: Dict[str, Any]) -> Dict[str, Any]:
    """Quick add event from natural language"""

    text = params.get("text", "")

    # Simple parsing (in real implementation would use NLP)
    event_id = f"event_{random.randint(1000, 9999)}"

    # Extract basic info from text
    summary = text.split(" at ")[0] if " at " in text else text

    # Default to next hour
    start_time = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    event = {
        "id": event_id,
        "summary": summary,
        "description": f"Created from: '{text}'",
        "start": {
            "dateTime": start_time.isoformat() + "Z",
            "timeZone": "Europe/Paris"
        },
        "end": {
            "dateTime": end_time.isoformat() + "Z",
            "timeZone": "Europe/Paris"
        },
        "status": "confirmed",
        "created": datetime.now().isoformat()
    }

    return {
        "event": event,
        "parsed_text": text,
        "message": f"Quick event '{summary}' created"
    }

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Google Calendar MCP Stub Server",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "invoke": "/invoke",
            "docs": "/docs"
        },
        "supported_tasks": [
            "list_events",
            "create_event",
            "update_event",
            "delete_event",
            "find_free_time",
            "get_busy_times",
            "quick_add"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 9102))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    print(f"🐚 Google Calendar MCP Stub Server starting on port {port}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        reload=False
    )