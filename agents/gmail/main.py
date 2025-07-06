#!/usr/bin/env python3
"""
GMailA - Email Operations Agent
Handles email operations via MCP server integration
Following clean architecture patterns from EXAMPLE_PY.md
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, get_llm_instance, voices, RunContext_T, to_greeter, BASE_INSTRUCTIONS
from livekit.agents import function_tool, FunctionTool
from livekit.plugins import groq
from typing import Annotated
from pydantic import Field

class GMailA(BaseAgent):
    """Gmail agent that handles email operations"""

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Alfred's Gmail agent Mike. Handle email operations briefly. "
                "Archive emails, create drafts, send messages.\n" +
                BASE_INSTRUCTIONS
            ),
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["gmail"]),
            tools=[to_greeter],
        )

    async def archive_promotional_emails_internal(self, context: RunContext_T) -> str:
        """Internal method to archive promotional emails"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Gmail operations
        # For now, return Batman-themed stub response
        archived_count = 2  # Batman demo scenario value
        userdata.archived_count = archived_count

        return f"Archived {archived_count} emails, sir."

    async def create_email_draft_internal(
        self,
        recipient: str,
        subject: str = "",
        content: str = "",
        context: RunContext_T = None,
    ) -> str:
        """Internal method to create email draft"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Gmail operations
        # For now, return Batman-themed stub response
        if not userdata.email_drafts:
            userdata.email_drafts = []
        if not userdata.email_recipients:
            userdata.email_recipients = []

        userdata.email_drafts.append(f"Draft for {recipient}: {subject}")
        userdata.email_recipients.append(recipient)

        # Batman narrative for demo scenario
        if recipient.lower() == "lucius":
            return f"Draft ready for Lucius, sir."

        return f"Draft created for {recipient}."

    async def send_email_internal(
        self,
        recipient: str,
        subject: str,
        content: str,
        context: RunContext_T,
    ) -> str:
        """Internal method to send email"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Gmail operations
        # For now, return Batman-themed stub response
        if not userdata.email_recipients:
            userdata.email_recipients = []

        userdata.email_recipients.append(recipient)

        return f"Message sent to {recipient}, sir."

    async def draft_urgent_replies_internal(self, context: RunContext_T) -> str:
        """Internal method to create draft replies for urgent messages"""
        userdata = context.userdata

        # AI-TODO: Integrate with actual MCP server for Gmail operations
        # For now, return Batman-themed stub response matching demo scenario
        urgent_count = 1  # Demo scenario shows "one draft created"
        if not userdata.email_drafts:
            userdata.email_drafts = []

        userdata.email_drafts.extend([
            "Draft reply to urgent Wayne Enterprises board meeting request"
        ])

        return f"One urgent draft created, sir."

    @function_tool()
    async def archive_promotional_emails(self, context: RunContext_T) -> str:
        """Archive promotional and spam emails from the inbox.
        This operation will move promotional emails to the archive folder."""
        agent = context.session.current_agent
        return await agent.archive_promotional_emails_internal(context)

    @function_tool()
    async def create_email_draft(
        self,
        recipient: Annotated[str, Field(description="Email recipient name or address")],
        subject: Annotated[str, Field(description="Email subject line")] = "",
        content: Annotated[str, Field(description="Email content/body")] = "",
        context: RunContext_T = None,
    ) -> str:
        """Create an email draft for the specified recipient.
        Confirm recipient and content with the user before creating."""
        agent = context.session.current_agent
        return await agent.create_email_draft_internal(recipient, subject, content, context)

    @function_tool()
    async def send_email(
        self,
        recipient: Annotated[str, Field(description="Email recipient name or address")],
        subject: Annotated[str, Field(description="Email subject line")],
        content: Annotated[str, Field(description="Email content/body")],
        context: RunContext_T,
    ) -> str:
        """Send an email to the specified recipient.
        Confirm all details with the user before sending."""
        agent = context.session.current_agent
        return await agent.send_email_internal(recipient, subject, content, context)

    @function_tool()
    async def draft_urgent_replies(self, context: RunContext_T) -> str:
        """Create draft replies for urgent messages in the inbox.
        This will identify urgent emails and create appropriate draft responses."""
        agent = context.session.current_agent
        return await agent.draft_urgent_replies_internal(context)
