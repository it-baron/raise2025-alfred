#!/usr/bin/env python3
"""
GreeterA - Edge Agent for Intent Detection and Routing
Handles voice input and routes to appropriate service agents
Following clean architecture patterns from EXAMPLE_PY.md
"""

from base_agent import BaseAgent, get_llm_instance, voices, RunContext_T
from instructions import GREETER_INSTRUCTIONS
from livekit.agents import Agent, function_tool
from livekit.plugins import groq

class GreeterA(BaseAgent):
    """Greeter agent that detects user intents and routes to appropriate agents"""

    def __init__(self) -> None:
        super().__init__(
            instructions=GREETER_INSTRUCTIONS,
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["greeter"])
        )


