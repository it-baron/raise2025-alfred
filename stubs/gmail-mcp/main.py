#!/usr/bin/env python3
"""
Gmail MCP Stub Server
Provides stubbed Gmail API responses for Phase 0 testing
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
    title="Gmail MCP Stub Server",
    description="Stubbed Gmail API responses for Alfred Phase 0",
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
SAMPLE_EMAILS = [
    {
        "id": "msg_001",
        "threadId": "thread_001",
        "from": "promotions@store.com",
        "to": "user@example.com",
        "subject": "🔥 50% OFF Everything - Limited Time!",
        "snippet": "Don't miss out on our biggest sale of the year...",
        "date": "2025-01-05T14:30:00Z",
        "labels": ["INBOX", "CATEGORY_PROMOTIONS"],
        "unread": True,
        "body": "Get 50% off everything in our store. Use code SAVE50 at checkout. Limited time offer!"
    },
    {
        "id": "msg_002",
        "threadId": "thread_002",
        "from": "boss@company.com",
        "to": "user@example.com",
        "subject": "URGENT: Project deadline moved up",
        "snippet": "Hi, we need to discuss the project timeline...",
        "date": "2025-01-05T09:15:00Z",
        "labels": ["INBOX", "IMPORTANT"],
        "unread": True,
        "body": "Hi, the client wants to move up the deadline to next Friday. Can we schedule a call to discuss?"
    },
    {
        "id": "msg_003",
        "threadId": "thread_003",
        "from": "newsletter@techblog.com",
        "to": "user@example.com",
        "subject": "Weekly Tech Digest - AI Advances",
        "snippet": "This week's top stories in artificial intelligence...",
        "date": "2025-01-05T08:00:00Z",
        "labels": ["INBOX", "CATEGORY_UPDATES"],
        "unread": False,
        "body": "This week's top stories: GPT-5 rumors, new robotics breakthroughs, and quantum computing updates."
    }
]

DRAFT_TEMPLATES = {
    "reply": "Thank you for your email. I'll get back to you shortly regarding {subject}.",
    "follow_up": "Following up on our previous conversation about {topic}.",
    "meeting": "I'd like to schedule a meeting to discuss {topic}. Are you available {timeframe}?",
    "update": "Here's an update on {project}: {status}"
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Gmail MCP Stub", "timestamp": datetime.now().isoformat()}

@app.post("/invoke", response_model=MCPResponse)
async def invoke_mcp(request: MCPRequest):
    """Main MCP invocation endpoint"""

    try:
        result = None
        message = "Operation completed successfully"

        if request.task == "list_emails":
            result = await list_emails(request.parameters)

        elif request.task == "archive":
            result = await archive_emails(request.parameters)

        elif request.task == "draft":
            result = await create_draft(request.parameters)

        elif request.task == "send":
            result = await send_email(request.parameters)

        elif request.task == "search":
            result = await search_emails(request.parameters)

        elif request.task == "mark_read":
            result = await mark_as_read(request.parameters)

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

async def list_emails(params: Dict[str, Any]) -> Dict[str, Any]:
    """List emails with optional filtering"""

    max_results = params.get("max_results", 10)
    label_filter = params.get("labels", [])
    unread_only = params.get("unread_only", False)

    emails = SAMPLE_EMAILS.copy()

    # Apply filters
    if label_filter:
        emails = [email for email in emails if any(label in email["labels"] for label in label_filter)]

    if unread_only:
        emails = [email for email in emails if email["unread"]]

    # Limit results
    emails = emails[:max_results]

    return {
        "emails": emails,
        "total_count": len(emails),
        "unread_count": len([e for e in emails if e["unread"]]),
        "has_more": False
    }

async def archive_emails(params: Dict[str, Any]) -> Dict[str, Any]:
    """Archive emails (promotions and newsletters)"""

    query = params.get("query", "category:promotions OR category:updates")

    # Simulate archiving promotional emails
    archived_emails = []
    for email in SAMPLE_EMAILS:
        if ("CATEGORY_PROMOTIONS" in email["labels"] or
            "CATEGORY_UPDATES" in email["labels"]):
            archived_emails.append({
                "id": email["id"],
                "subject": email["subject"],
                "from": email["from"]
            })

    return {
        "archived_count": len(archived_emails),
        "archived_emails": archived_emails,
        "query_used": query
    }

async def create_draft(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create email draft"""

    to = params.get("to", "")
    subject = params.get("subject", "")
    body = params.get("body", "")
    template = params.get("template", "reply")
    context = params.get("context", {})

    # Generate draft content if not provided
    if not body and template in DRAFT_TEMPLATES:
        body = DRAFT_TEMPLATES[template].format(**context)

    draft_id = f"draft_{random.randint(1000, 9999)}"

    draft = {
        "id": draft_id,
        "to": to,
        "subject": subject,
        "body": body,
        "created": datetime.now().isoformat(),
        "status": "draft"
    }

    return {
        "draft": draft,
        "message": f"Draft created for {to}"
    }

async def send_email(params: Dict[str, Any]) -> Dict[str, Any]:
    """Send email"""

    to = params.get("to", "")
    subject = params.get("subject", "")
    body = params.get("body", "")
    draft_id = params.get("draft_id")

    message_id = f"msg_{random.randint(10000, 99999)}"

    return {
        "message_id": message_id,
        "to": to,
        "subject": subject,
        "sent_at": datetime.now().isoformat(),
        "status": "sent"
    }

async def search_emails(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search emails by query"""

    query = params.get("query", "")
    max_results = params.get("max_results", 10)

    # Simple search simulation
    results = []
    for email in SAMPLE_EMAILS:
        if (query.lower() in email["subject"].lower() or
            query.lower() in email["body"].lower() or
            query.lower() in email["from"].lower()):
            results.append(email)

    return {
        "results": results[:max_results],
        "query": query,
        "total_found": len(results)
    }

async def mark_as_read(params: Dict[str, Any]) -> Dict[str, Any]:
    """Mark emails as read"""

    email_ids = params.get("email_ids", [])

    return {
        "marked_read": email_ids,
        "count": len(email_ids),
        "status": "completed"
    }

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Gmail MCP Stub Server",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "invoke": "/invoke",
            "docs": "/docs"
        },
        "supported_tasks": [
            "list_emails",
            "archive",
            "draft",
            "send",
            "search",
            "mark_read"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 9101))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    print(f"🐚 Gmail MCP Stub Server starting on port {port}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        reload=False
    )