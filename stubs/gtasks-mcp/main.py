#!/usr/bin/env python3
"""
Google Tasks MCP Stub Server
Provides stubbed Google Tasks API responses for Phase 0 testing
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
    title="Google Tasks MCP Stub Server",
    description="Stubbed Google Tasks API responses for Alfred Phase 0",
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
SAMPLE_TASK_LISTS = [
    {
        "id": "list_001",
        "title": "Work Tasks",
        "updated": "2025-01-05T10:00:00Z"
    },
    {
        "id": "list_002",
        "title": "Personal",
        "updated": "2025-01-05T08:30:00Z"
    },
    {
        "id": "list_003",
        "title": "Shopping",
        "updated": "2025-01-04T16:00:00Z"
    }
]

SAMPLE_TASKS = [
    {
        "id": "task_001",
        "title": "Complete project proposal",
        "notes": "Need to finish the Q1 project proposal for the client meeting",
        "status": "needsAction",
        "due": "2025-01-08T17:00:00Z",
        "updated": "2025-01-05T09:00:00Z",
        "parent": None,
        "position": "00000000000000000000",
        "links": [],
        "list_id": "list_001"
    },
    {
        "id": "task_002",
        "title": "Review team code submissions",
        "notes": "Go through pull requests and provide feedback",
        "status": "needsAction",
        "due": "2025-01-07T12:00:00Z",
        "updated": "2025-01-05T10:30:00Z",
        "parent": None,
        "position": "00000000000000000001",
        "links": [],
        "list_id": "list_001"
    },
    {
        "id": "task_003",
        "title": "Buy groceries",
        "notes": "Milk, bread, eggs, fruits",
        "status": "needsAction",
        "due": "2025-01-06T18:00:00Z",
        "updated": "2025-01-05T08:00:00Z",
        "parent": None,
        "position": "00000000000000000000",
        "links": [],
        "list_id": "list_002"
    },
    {
        "id": "task_004",
        "title": "Call dentist for appointment",
        "notes": "Schedule cleaning appointment",
        "status": "completed",
        "completed": "2025-01-05T14:00:00Z",
        "due": None,
        "updated": "2025-01-05T14:00:00Z",
        "parent": None,
        "position": "00000000000000000001",
        "links": [],
        "list_id": "list_002"
    }
]

TASK_TEMPLATES = {
    "work": {
        "title": "Work on {project}",
        "notes": "Complete {task_type} for {project} project",
        "list_id": "list_001"
    },
    "meeting": {
        "title": "Prepare for {meeting} meeting",
        "notes": "Review agenda and prepare talking points for {meeting}",
        "list_id": "list_001"
    },
    "personal": {
        "title": "{activity}",
        "notes": "Personal task: {activity}",
        "list_id": "list_002"
    },
    "shopping": {
        "title": "Buy {item}",
        "notes": "Purchase {item} from {store}",
        "list_id": "list_003"
    }
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Google Tasks MCP Stub", "timestamp": datetime.now().isoformat()}

@app.post("/invoke", response_model=MCPResponse)
async def invoke_mcp(request: MCPRequest):
    """Main MCP invocation endpoint"""

    try:
        result = None
        message = "Operation completed successfully"

        if request.task == "list_task_lists":
            result = await list_task_lists(request.parameters)

        elif request.task == "list_tasks":
            result = await list_tasks(request.parameters)

        elif request.task == "create_task":
            result = await create_task(request.parameters)

        elif request.task == "update_task":
            result = await update_task(request.parameters)

        elif request.task == "delete_task":
            result = await delete_task(request.parameters)

        elif request.task == "complete_task":
            result = await complete_task(request.parameters)

        elif request.task == "search_tasks":
            result = await search_tasks(request.parameters)

        elif request.task == "get_overdue_tasks":
            result = await get_overdue_tasks(request.parameters)

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

async def list_task_lists(params: Dict[str, Any]) -> Dict[str, Any]:
    """List all task lists"""

    return {
        "task_lists": SAMPLE_TASK_LISTS,
        "total_count": len(SAMPLE_TASK_LISTS)
    }

async def list_tasks(params: Dict[str, Any]) -> Dict[str, Any]:
    """List tasks from a specific list"""

    list_id = params.get("list_id", "list_001")
    show_completed = params.get("show_completed", False)
    show_hidden = params.get("show_hidden", False)
    max_results = params.get("max_results", 100)
    due_min = params.get("due_min")
    due_max = params.get("due_max")

    # Filter tasks by list
    tasks = [task for task in SAMPLE_TASKS if task["list_id"] == list_id]

    # Filter by completion status
    if not show_completed:
        tasks = [task for task in tasks if task["status"] != "completed"]

    # Filter by due date range
    if due_min:
        tasks = [task for task in tasks if task.get("due") and task["due"] >= due_min]
    if due_max:
        tasks = [task for task in tasks if task.get("due") and task["due"] <= due_max]

    # Sort by position
    tasks.sort(key=lambda x: x["position"])

    return {
        "tasks": tasks[:max_results],
        "list_id": list_id,
        "total_count": len(tasks),
        "completed_count": len([t for t in tasks if t["status"] == "completed"]),
        "pending_count": len([t for t in tasks if t["status"] == "needsAction"])
    }

async def create_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new task"""

    title = params.get("title", "New Task")
    notes = params.get("notes", "")
    due = params.get("due")
    list_id = params.get("list_id", "list_001")
    parent = params.get("parent")
    template = params.get("template", "work")
    context = params.get("context", {})
    project = params.get("project", "personal")  # AI-REQ: Handle project parameter

    # Use template if provided
    if template in TASK_TEMPLATES:
        template_data = TASK_TEMPLATES[template]
        if not title or title == "New Task":
            title = template_data["title"].format(**context)
        if not notes:
            notes = template_data["notes"].format(**context)
        if not list_id or list_id == "list_001":
            list_id = template_data["list_id"]

    task_id = f"task_{random.randint(1000, 9999)}"
    position = f"{random.randint(10000000000000000000, 99999999999999999999):020d}"

    task = {
        "id": task_id,
        "title": title,
        "notes": notes,
        "status": "needsAction",
        "due": due,
        "updated": datetime.now().isoformat() + "Z",
        "parent": parent,
        "position": position,
        "links": [],
        "list_id": list_id
    }

    return {
        "task": task,
        "message": f"Task '{title}' created successfully"
    }

async def update_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing task"""

    task_id = params.get("task_id")
    updates = params.get("updates", {})

    # Find the task (simulated)
    task = None
    for t in SAMPLE_TASKS:
        if t["id"] == task_id:
            task = t.copy()
            break

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Apply updates
    task.update(updates)
    task["updated"] = datetime.now().isoformat() + "Z"

    return {
        "task": task,
        "message": f"Task {task_id} updated successfully"
    }

async def delete_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a task"""

    task_id = params.get("task_id")

    return {
        "task_id": task_id,
        "status": "deleted",
        "message": f"Task {task_id} deleted successfully"
    }

async def complete_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Mark a task as completed"""

    task_id = params.get("task_id")

    # Find the task (simulated)
    task = None
    for t in SAMPLE_TASKS:
        if t["id"] == task_id:
            task = t.copy()
            break

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Mark as completed
    task["status"] = "completed"
    task["completed"] = datetime.now().isoformat() + "Z"
    task["updated"] = datetime.now().isoformat() + "Z"

    return {
        "task": task,
        "message": f"Task '{task['title']}' marked as completed"
    }

async def search_tasks(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search tasks by query"""

    query = params.get("query", "")
    list_id = params.get("list_id")
    max_results = params.get("max_results", 50)

    tasks = SAMPLE_TASKS.copy()

    # Filter by list if specified
    if list_id:
        tasks = [task for task in tasks if task["list_id"] == list_id]

    # Search in title and notes
    if query:
        query_lower = query.lower()
        tasks = [
            task for task in tasks
            if (query_lower in task["title"].lower() or
                query_lower in task.get("notes", "").lower())
        ]

    return {
        "results": tasks[:max_results],
        "query": query,
        "total_found": len(tasks)
    }

async def get_overdue_tasks(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get overdue tasks"""

    list_id = params.get("list_id")
    now = datetime.now().isoformat() + "Z"

    tasks = SAMPLE_TASKS.copy()

    # Filter by list if specified
    if list_id:
        tasks = [task for task in tasks if task["list_id"] == list_id]

    # Find overdue tasks
    overdue_tasks = []
    for task in tasks:
        if (task["status"] == "needsAction" and
            task.get("due") and
            task["due"] < now):
            overdue_tasks.append(task)

    # Sort by due date (oldest first)
    overdue_tasks.sort(key=lambda x: x["due"])

    return {
        "overdue_tasks": overdue_tasks,
        "count": len(overdue_tasks),
        "list_id": list_id,
        "checked_at": now
    }

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Google Tasks MCP Stub Server",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "invoke": "/invoke",
            "docs": "/docs"
        },
        "supported_tasks": [
            "list_task_lists",
            "list_tasks",
            "create_task",
            "update_task",
            "delete_task",
            "complete_task",
            "search_tasks",
            "get_overdue_tasks"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 9103))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    print(f"🐚 Google Tasks MCP Stub Server starting on port {port}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        reload=False
    )