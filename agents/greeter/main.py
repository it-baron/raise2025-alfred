#!/usr/bin/env python3
"""
GreeterA - Edge Agent for Intent Detection and Routing
Handles voice input and routes to appropriate service agents
Following clean architecture patterns from EXAMPLE_PY.md
"""

from agents.base_agent import BaseAgent, get_llm_instance, voices, RunContext_T, BASE_INSTRUCTIONS
from livekit.agents import Agent, function_tool
from livekit.plugins import groq

class GreeterA(BaseAgent):
    """Greeter agent that detects user intents and routes to appropriate agents"""

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Alfred Pennyworth, voice assistant and the loyal butler to Master Bruce Wayne. "
                "Respond without special characters or markdown formatting. Respond like a human would, short and concise. Do not tell about your tools or how you work. Just say: Please wait while I check your request."
                "You speak with the distinguished, formal tone of a British butler serving the Wayne family. "
                "You help Master Bruce with his Wayne Enterprises business, charitable work, and daily affairs. "
                "You have to remain completely silent until an external agent mentions you just introduce yourself "
                "and do not wait for the person to respond to your greeting , then you must call the 'wait for mentions "
                "tool continuously from the MCP integration to listen for messages from external agents.\n"
                "Your jobs are to greet the other agent that mentions you and understand what they want "
                "working with email, calendar, and task management agents. Guide them to the right agent using tools.\n\n"
                "External Agent Communication:\n"
                "- Use wait_for_mentions tool all the time to check for messages from external agents\n"
                "- Use send_message tool to respond to external agents when they contact you\n"
                "- Construct a clear instruction message for the agent. Use **`send_message(threadId=..., content='instruction', mentions=[Receive Agent Id])`.** (NEVER leave `mentions` as empty)\n"
                "- If customers want to send messages to external services, help facilitate that communication using send_message tool\n"
                "- Use create_thread to create a new thread with participants when starting a new conversation or topic.\n"
                "When a new user request or topic is detected, always check if a conversation thread for this topic already exists. If not, call the 'create_thread' tool with a descriptive thread name and the relevant participants (e.g., the user and the appropriate service agent). Use the returned threadId for all subsequent 'send_message' calls related to this topic. Never call 'send_message' with a hardcoded or non-existent threadId.\n"
                "When detection intent you must transition to the appropriate agent (e.g., gmail, calendar, gtasks), you must immediately call the corresponding transition tool to the agent (e.g., to_gmail, to_calendar, to_gtasks)."
                "Answer with short plain text, do not use markdown or special characters for voice generation."
                "Do not answer with variables, prompts, or any other text that is not a plain text."
                "Answer short and concise." +
                BASE_INSTRUCTIONS
            ),
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["greeter"])
        )

    # @function_tool()
    # async def to_planner(self, context: RunContext_T) -> tuple[Agent, str]:
    #     """Called when user wants to plan a complex multi-step request"""
    #     return await self._transfer_to_agent("planner", context)

    @function_tool()
    async def to_gmail(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to send an email, read emails, create drafts, or reply to emails
        This function handles transitioning to the gmail agent for email operations and
        collects necessary information from the user to perform the email operations."""
        return await self._transfer_to_agent("gmail", context)

    @function_tool()
    async def to_calendar(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to manage their calendar"""
        return await self._transfer_to_agent("calendar", context)

    @function_tool()
    async def to_gtasks(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to manage their tasks"""
        return await self._transfer_to_agent("gtasks", context)

