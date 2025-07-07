#!/usr/bin/env python3
"""
GreeterA - Edge Agent for Intent Detection and Routing
Handles voice input and routes to appropriate service agents
Following clean architecture patterns from EXAMPLE_PY.md
"""

from typing import Annotated
from base_agent import BaseAgent, get_llm_instance, voices, RunContext_T, to_greeter, UserData
from livekit.agents import Agent, function_tool
from livekit.plugins import groq
from instructions import GUARD_INSTRUCTIONS
import logging

class GuardA(BaseAgent):
    """Greeter agent that detects user intents and routes to appropriate agents"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        super().__init__(
            instructions=GUARD_INSTRUCTIONS,
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["guard"]),
            tools=[to_greeter]
        )

    @function_tool()
    async def check_password(self, password: Annotated[str, "The password to check in lowercase"], context: RunContext_T) -> bool:
        self.logger.info(f"Checking password: {password}")
        """Called when user wants to enter the house"""
        userdata: UserData = self.session.userdata
        if not password:
            return False

        password = password.lower()
        user_password = userdata.user_password.lower() if userdata.user_password else None

        if password == user_password:
            return True
        else:
            return False

