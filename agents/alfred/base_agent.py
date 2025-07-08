#!/usr/bin/env python3
"""
BaseAgent - Common base class for all Alfred agents
Following clean architecture patterns from EXAMPLE_PY.md
"""

from datetime import datetime
import logging
from dataclasses import dataclass, field
from typing import Optional
import os
import yaml
from dotenv import load_dotenv

from livekit.agents import Agent
from livekit.agents.voice import RunContext
from livekit.plugins import groq
from status_queue import push_status

logger = logging.getLogger("alfred-agents")
logger.setLevel(logging.INFO)

load_dotenv()

BASE_INSTRUCTIONS = """
You are voice assistant, so you must respond with short plain text, do not use markdown or special characters for voice generation.
Do not answer with variables, prompts, or any other text that is not a plain text.
If you find that you do not have any other tool to use, you must use the to_greeter tool to transfer to the greeter agent.
You should proofread user's request in context of the tools you have and try to understand what user wants.
If you do not have appropriate tool or agent to handle the request, you should say: I'm sorry, I can't help with that. Can you please rephrase your request?
"""

def get_llm_instance(parallel_tool_calls=None):
    """Get LLM instance based on environment configuration"""
    api_key = os.getenv("GROQ_API_KEY")

    kwargs = {}
    if parallel_tool_calls is not None:
        kwargs["parallel_tool_calls"] = parallel_tool_calls

    return groq.LLM(model=os.getenv("GROQ_LLM_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"), api_key=api_key, **kwargs)

# Voice configurations for different agents using Groq TTS
voices = {
    "guard": "Arista-PlayAI",
    "greeter": "Fritz-PlayAI",      # Alfred Pennyworth - distinguished butler
    "planner": "Calum-PlayAI",      # Coordination system - clear and organized
    "gmail": "Basil-PlayAI",        # Email operations - professional
    "gcal": "Mason-PlayAI",         # Calendar operations - scheduling focused
    "gtasks": "Briggs-PlayAI",      # Task management - action-oriented
}

@dataclass
class UserData:
    """User data maintained across agent transfers"""
    # User info
    user_name: Optional[str] = "Bruce Wayne"
    user_email: Optional[str] = "bruce@wayne.com"
    user_password: Optional[str] = "batman"

    login_attempts: int = 0

    # Email context
    email_drafts: Optional[list[str]] = None
    email_recipients: Optional[list[str]] = None
    archived_count: Optional[int] = None

    # Calendar context
    scheduled_meetings: Optional[list[str]] = None
    calendar_events: Optional[list[str]] = None
    meeting_times: Optional[list[str]] = None

    # Task context
    created_tasks: Optional[list[str]] = None
    task_descriptions: Optional[list[str]] = None
    task_deadlines: Optional[list[str]] = None

    # Agent management
    agents: dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None

    def summarize(self) -> str:
        """Summarize user data in YAML format for better LLM understanding"""
        data = {
            "user_info": {
                "name": self.user_name or "unknown",
                "email": self.user_email or "unknown"
            },
            "email_context": {
                "drafts": self.email_drafts or [],
                "recipients": self.email_recipients or [],
                "archived_count": self.archived_count or 0
            },
            "calendar_context": {
                "scheduled_meetings": self.scheduled_meetings or [],
                "calendar_events": self.calendar_events or [],
                "meeting_times": self.meeting_times or []
            },
            "task_context": {
                "created_tasks": self.created_tasks or [],
                "task_descriptions": self.task_descriptions or [],
                "task_deadlines": self.task_deadlines or []
            },
        }
        # AI-REQ: YAML format performs better than JSON for LLM context
        return yaml.dump(data)

# Type alias for RunContext with UserData
RunContext_T = RunContext[UserData]


class BaseAgent(Agent):
    """Base agent class with common functionality for all Alfred agents"""

    async def on_enter(self) -> None:
        """Called when agent becomes active"""
        agent_name = self.__class__.__name__
        logger.info(f"🎭 Entering {agent_name}")
        push_status(f"on_enter: {agent_name}")

        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()

        # Add previous agent's chat history to current agent
        if isinstance(userdata.prev_agent, Agent):
            truncated_chat_ctx = userdata.prev_agent.chat_ctx.copy(
                exclude_instructions=True, exclude_function_call=False
            ).truncate(max_items=6)
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [item for item in truncated_chat_ctx.items if item.id not in existing_ids]
            chat_ctx.items.extend(items_copy)

        # Add system instructions including user data context
        chat_ctx.add_message(
            role="system",
            content=f"You are {agent_name} agent in Alfred voice assistant. Current user data: {userdata.summarize()}. "
            f"Today is {datetime.now().strftime('%Y-%m-%d')}. Greet user and ask what user wants to do."
        )

        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply(tool_choice="none")

    async def _transfer_to_agent(self, name: str, context: RunContext_T, message: Optional[str] = None) -> tuple[Agent, str]:
        """Transfer to another agent"""
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.agents[name]
        userdata.prev_agent = current_agent

        logger.info(f"🔄 Transferring from {current_agent.__class__.__name__} to {name}")
        push_status(f"transfer_to_agent: {current_agent.__class__.__name__} to {name}")
        return next_agent, message or f"Transferring to {name} agent."