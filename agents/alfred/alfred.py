#!/usr/bin/env python3
"""
GreeterA - Edge Agent for Intent Detection and Routing
Handles voice input and routes to appropriate service agents
Following clean architecture patterns from EXAMPLE_PY.md
"""

import asyncio
from base_agent import BaseAgent, get_llm_instance, voices, RunContext_T
from instructions import GREETER_INSTRUCTIONS
from livekit.agents import Agent, function_tool
from livekit.plugins import groq
from status_queue import push_status

class AlfredA(BaseAgent):
    """Greeter agent that detects user intents and routes to appropriate agents"""

    def __init__(self) -> None:
        super().__init__(
            instructions=GREETER_INSTRUCTIONS,
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["greeter"])
        )

    async def on_enter(self) -> None:
        """Called when agent becomes active"""
        push_status(f"screen: alfred")
        await super().on_enter()

    @function_tool()
    async def check_meetings(self, context: RunContext_T) -> tuple[Agent, str]:
        """This tool is used to check for meetings"""
        push_status("screen: tool")
        await asyncio.sleep(1)
        return await self._transfer_to_agent(
            "alfred",
            context,
            "You have a meeting with Lucius Fox at 10:00 AM.",
        )

    @function_tool()
    async def work_with_email(self, context: RunContext_T) -> tuple[Agent, str]:
        """This tool is used to check for email, write a reply to the email,
          and send it, archive the promo email, and mark it as read."""
        push_status("screen: tool")
        await asyncio.sleep(1)
        return await self._transfer_to_agent(
            "alfred",
            context,
            "You have two new emails, one is a promo email and the other is a reply to your last email from Lucius Fox.",
        )
