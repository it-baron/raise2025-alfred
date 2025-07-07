#!/usr/bin/env python3
"""
Coordinator Agent - A2A Protocol Implementation
Handles agent discovery, registration, and message routing
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
from docker.errors import DockerException
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coordinator")

# Initialize FastAPI app
app = FastAPI(
    title="Alfred Coordinator Agent",
    description="Central orchestration service for A2A protocol",
    version="0.1.0"
)

# In-memory agent registry
# Structure: {agent_name: {"card": AgentCard, "url": str, "last_seen": datetime}}
agent_registry: Dict[str, Dict[str, Any]] = {}

# Skill to agent mapping
# Structure: {skill_id: {"agent_name": str, "agent_url": str, "description": str}}
skill_registry: Dict[str, Dict[str, Any]] = {}

# Models
class HealthResponse(BaseModel):
    status: str
    agents: int
    timestamp: str


class AgentCard(BaseModel):
    """A2A Agent Card structure"""
    name: str
    description: str
    provider: Dict[str, str]
    url: str
    version: str
    capabilities: Dict[str, bool]
    authentication: Dict[str, Any]
    skills: list[Dict[str, Any]]


class SkillsResponse(BaseModel):
    """Response model for /skills endpoint"""
    skills: Dict[str, Dict[str, str]]
    totalAgents: int
    lastUpdated: str


class MessageRequest(BaseModel):
    """Request model for sending messages"""
    role: str = "user"
    parts: List[Dict[str, Any]]
    messageId: str
    contextId: Optional[str] = None
    sessionId: Optional[str] = None
    referenceTaskIds: Optional[List[str]] = None


class MessageResponse(BaseModel):
    """Response model for message processing"""
    messageId: str
    contextId: str
    intent: Optional[str] = None
    targetSkill: Optional[str] = None
    targetAgent: Optional[str] = None
    status: str
    message: str


@app.get("/.well-known/agent.json", response_model=AgentCard)
async def get_agent_card():
    """Return coordinator's A2A agent card"""
    return AgentCard(
        name="alfred-coordinator",
        description="Central orchestration agent for Alfred voice assistant system",
        provider={
            "name": "Alfred System",
            "url": "https://alfred.example.com"
        },
        url=f"http://localhost:{os.getenv('COORDINATOR_PORT', '8080')}",
        version="0.1.0",
        capabilities={
            "streaming": False,  # Will add SSE support later
            "pushNotifications": False
        },
        authentication={
            "schemes": ["Bearer", "ApiKey"]
        },
        skills=[
            {
                "id": "route_message",
                "name": "Message Routing",
                "description": "Route messages to appropriate service agents",
                "inputModes": ["text"],
                "outputModes": ["text"],
                "examples": [
                    "Archive all promotional emails",
                    "Schedule a meeting with John tomorrow",
                    "Create a task to buy groceries"
                ]
            },
            {
                "id": "discover_skills",
                "name": "Skill Discovery",
                "description": "Discover available skills across all registered agents",
                "inputModes": ["text"],
                "outputModes": ["text"],
                "examples": ["What can you do?", "List available skills"]
            }
        ]
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        agents=len(agent_registry),
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/skills", response_model=SkillsResponse)
async def get_skills():
    """Get all available skills across registered agents"""
    # Build skills response
    skills_dict = {}

    for skill_id, skill_info in skill_registry.items():
        skills_dict[skill_id] = {
            "agentName": skill_info["agent_name"],
            "agentUrl": skill_info["agent_url"],
            "description": skill_info["description"],
            "skillName": skill_info.get("skill_name", skill_id)
        }

    return SkillsResponse(
        skills=skills_dict,
        totalAgents=len(agent_registry),
        lastUpdated=datetime.utcnow().isoformat()
    )


@app.get("/agents")
async def get_agents():
    """Get all registered agents"""
    agents_list = []

    for agent_name, agent_info in agent_registry.items():
        agents_list.append({
            "name": agent_name,
            "url": agent_info["url"],
            "lastSeen": agent_info["last_seen"].isoformat(),
            "skills": [skill["id"] for skill in agent_info["card"].get("skills", [])]
        })

    return {
        "agents": agents_list,
        "total": len(agents_list),
        "timestamp": datetime.utcnow().isoformat()
    }


def extract_intent_from_message(message_request: MessageRequest) -> Dict[str, Any]:
    """Extract intent and identify target skill from message"""
    # Extract text from parts
    text_content = ""
    for part in message_request.parts:
        if part.get("kind") == "text":
            text_content += part.get("text", "") + " "

    text_content = text_content.strip().lower()

    # Simple keyword-based intent detection
    intent_mapping = {
        "archive": {"intent": "archive_emails", "skill": "archive_emails"},
        "email": {"intent": "email_operation", "skill": "archive_emails"},
        "draft": {"intent": "create_draft", "skill": "draft_email"},
        "reply": {"intent": "create_draft", "skill": "draft_email"},
        "schedule": {"intent": "schedule_meeting", "skill": "schedule_meeting"},
        "meeting": {"intent": "schedule_meeting", "skill": "schedule_meeting"},
        "calendar": {"intent": "calendar_operation", "skill": "create_event"},
        "event": {"intent": "create_event", "skill": "create_event"},
        "task": {"intent": "create_task", "skill": "create_task"},
        "todo": {"intent": "create_todo", "skill": "create_todo"},
        "reminder": {"intent": "set_reminder", "skill": "set_reminder"}
    }

    # Find matching intent
    detected_intent = None
    target_skill = None

    for keyword, mapping in intent_mapping.items():
        if keyword in text_content:
            detected_intent = mapping["intent"]
            target_skill = mapping["skill"]
            break

    return {
        "intent": detected_intent,
        "skill": target_skill,
        "text": text_content
    }


@app.post("/send-message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Process incoming message and route to appropriate agent"""
    logger.info(f"📨 Received message: {request.messageId}")

    # Generate or use existing context ID
    context_id = request.contextId or f"ctx-{datetime.utcnow().timestamp()}"

    # Extract intent from message
    intent_info = extract_intent_from_message(request)

    # Find target agent for the skill
    target_agent = None
    target_agent_url = None

    if intent_info["skill"] and intent_info["skill"] in skill_registry:
        skill_info = skill_registry[intent_info["skill"]]
        target_agent = skill_info["agent_name"]
        target_agent_url = skill_info["agent_url"]

    # For now, just return the parsed intent without routing
    response_message = f"Intent: {intent_info['intent']}, Target: {target_agent or 'none'}"

    if not intent_info["intent"]:
        response_message = "Could not understand the request. Please try again."
    elif not target_agent:
        response_message = f"No agent available for skill: {intent_info['skill']}"
    else:
        response_message = f"Would route to {target_agent} for {intent_info['intent']}"

    return MessageResponse(
        messageId=request.messageId,
        contextId=context_id,
        intent=intent_info["intent"],
        targetSkill=intent_info["skill"],
        targetAgent=target_agent,
        status="parsed" if intent_info["intent"] else "unknown",
        message=response_message
    )


def register_agent(agent_name: str, agent_card: Dict[str, Any], agent_url: str):
    """Register an agent and its skills in the registry"""
    logger.info(f"📝 Registering agent: {agent_name} at {agent_url}")

    # Store agent info
    agent_registry[agent_name] = {
        "card": agent_card,
        "url": agent_url,
        "last_seen": datetime.utcnow()
    }

    # Extract and register skills
    for skill in agent_card.get("skills", []):
        skill_id = skill.get("id")
        if skill_id:
            skill_registry[skill_id] = {
                "agent_name": agent_name,
                "agent_url": agent_url,
                "description": skill.get("description", ""),
                "skill_name": skill.get("name", skill_id)
            }
            logger.info(f"  ✅ Registered skill: {skill_id}")

    logger.info(f"✨ Agent {agent_name} registered with {len(agent_card.get('skills', []))} skills")


def unregister_agent(agent_name: str):
    """Remove an agent and its skills from the registry"""
    logger.info(f"🗑️ Unregistering agent: {agent_name}")

    # Remove skills associated with this agent
    skills_to_remove = [
        skill_id for skill_id, info in skill_registry.items()
        if info["agent_name"] == agent_name
    ]

    for skill_id in skills_to_remove:
        del skill_registry[skill_id]
        logger.info(f"  ❌ Removed skill: {skill_id}")

    # Remove agent
    if agent_name in agent_registry:
        del agent_registry[agent_name]

    logger.info(f"✨ Agent {agent_name} unregistered")


def get_docker_client():
    """Get Docker client instance"""
    try:
        # Try to connect to Docker
        client = docker.from_env()
        client.ping()
        return client
    except DockerException as e:
        logger.error(f"❌ Failed to connect to Docker: {e}")
        return None


def discover_agent_containers() -> List[Dict[str, Any]]:
    """Discover containers with agent=true label"""
    client = get_docker_client()
    if not client:
        return []

    try:
        # Find containers with agent=true label
        containers = client.containers.list(
            filters={"label": "agent=true"}
        )

        agent_containers = []
        for container in containers:
            # Get container info
            container_info = {
                "name": container.name,
                "id": container.short_id,
                "status": container.status,
                "labels": container.labels,
                "network": None
            }

            # Try to get network info
            if container.attrs.get("NetworkSettings", {}).get("Networks"):
                # Get the first network (usually bridge or custom)
                network_name = list(container.attrs["NetworkSettings"]["Networks"].keys())[0]
                network_info = container.attrs["NetworkSettings"]["Networks"][network_name]
                container_info["network"] = {
                    "name": network_name,
                    "ip": network_info.get("IPAddress", ""),
                    "aliases": network_info.get("Aliases", [])
                }

            agent_containers.append(container_info)
            logger.info(f"🐳 Found agent container: {container.name} ({container.short_id})")

        return agent_containers

    except Exception as e:
        logger.error(f"❌ Error discovering containers: {e}")
        return []


async def fetch_agent_card(container_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fetch agent card from container"""
    container_name = container_info["name"]

    # Try different URL patterns
    urls_to_try = []

    # If we have network info with IP
    if container_info.get("network") and container_info["network"].get("ip"):
        ip = container_info["network"]["ip"]
        urls_to_try.append(f"http://{ip}:8080/.well-known/agent.json")
        urls_to_try.append(f"http://{ip}:8000/.well-known/agent.json")

    # Try container name (works in Docker networks)
    urls_to_try.append(f"http://{container_name}:8080/.well-known/agent.json")
    urls_to_try.append(f"http://{container_name}:8000/.well-known/agent.json")

    # Check if container has a custom port label
    port = container_info.get("labels", {}).get("agent.port", "8080")
    if port != "8080":
        if container_info.get("network") and container_info["network"].get("ip"):
            urls_to_try.insert(0, f"http://{container_info['network']['ip']}:{port}/.well-known/agent.json")
        urls_to_try.insert(0, f"http://{container_name}:{port}/.well-known/agent.json")

    async with httpx.AsyncClient(timeout=5.0) as client:
        for url in urls_to_try:
            try:
                logger.info(f"🔍 Trying to fetch agent card from: {url}")
                response = await client.get(url)

                if response.status_code == 200:
                    agent_card = response.json()
                    logger.info(f"✅ Successfully fetched agent card from {container_name}")
                    return agent_card

            except Exception as e:
                logger.debug(f"Failed to fetch from {url}: {e}")
                continue

    logger.warning(f"⚠️ Could not fetch agent card from container {container_name}")
    return None


async def discover_and_register_agents():
    """Discover agent containers and register them"""
    logger.info("🔍 Starting agent discovery...")

    # Get list of agent containers
    containers = discover_agent_containers()
    logger.info(f"Found {len(containers)} agent containers")

    # Fetch agent cards and register
    for container in containers:
        agent_card = await fetch_agent_card(container)
        if agent_card:
            # Use container name as agent name
            agent_name = agent_card.get("name", container["name"])

            # Determine agent URL
            agent_url = agent_card.get("url")
            if not agent_url:
                # Construct URL from container info
                if container.get("network") and container["network"].get("ip"):
                    port = container.get("labels", {}).get("agent.port", "8080")
                    agent_url = f"http://{container['network']['ip']}:{port}"
                else:
                    port = container.get("labels", {}).get("agent.port", "8080")
                    agent_url = f"http://{container['name']}:{port}"

            # Register the agent
            register_agent(agent_name, agent_card, agent_url)

    logger.info(f"✨ Agent discovery complete. Registered {len(agent_registry)} agents")


@app.on_event("startup")
async def startup_event():
    """Initialize coordinator on startup"""
    logger.info("🚀 Coordinator starting up...")
    logger.info("📍 Ready to discover agents")

    # Test Docker connection
    client = get_docker_client()
    if client:
        logger.info("✅ Docker connection established")
        # Start initial agent discovery
        await discover_and_register_agents()
    else:
        logger.warning("⚠️ Docker connection failed - agent discovery disabled")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("COORDINATOR_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)