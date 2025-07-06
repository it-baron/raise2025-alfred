#!/usr/bin/env python3
"""
PlannerA - Central Orchestration Agent
Handles complex multi-step workflows and coordinates between service agents
Following clean architecture patterns from EXAMPLE_PY.md
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, get_llm_instance, voices, RunContext_T, to_greeter, BASE_INSTRUCTIONS
from livekit.agents import Agent, function_tool
from livekit.plugins import groq

class PlannerA(BaseAgent):
    """Planner agent that orchestrates complex multi-step workflows"""

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Alfred's helper Mark. Handle complex workflows briefly.\n" +
                "Break requests into steps, route to agents, provide short summaries.\n" +
                "Available: Gmail, Calendar, GTasks agents.\n" +
                BASE_INSTRUCTIONS
            ),
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["planner"]),
            tools=[to_greeter],
        )

    @function_tool()
    async def plan_to_gmail(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to send an email, read emails, create drafts, or reply to emails
        This function handles transitioning to the gmail agent for email operations and
        collects necessary information from the user to perform the email operations."""
        return await self._transfer_to_agent("gmail", context)

    @function_tool()
    async def plan_to_calendar(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to manage their calendar"""
        return await self._transfer_to_agent("calendar", context)

    @function_tool()
    async def plan_to_gtasks(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to manage their tasks"""
        return await self._transfer_to_agent("gtasks", context)
