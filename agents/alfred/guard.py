#!/usr/bin/env python3
"""
GuardA - Guard agent for Alfred voice assistant
Handles voice input and routes to appropriate service agents
"""
import asyncio
from typing import Annotated, Optional
from base_agent import get_llm_instance, voices, RunContext_T, UserData
from livekit.agents import Agent, function_tool
from livekit.plugins import groq
from instructions import GUARD_INSTRUCTIONS
import logging
from status_queue import push_status

count = 0

class GuardA(Agent):
    """Guard agent that detects user intents and routes to appropriate agents"""
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        super().__init__(
            instructions=GUARD_INSTRUCTIONS,
            llm=get_llm_instance(parallel_tool_calls=False),
            tts=groq.TTS(voice=voices["guard"]),
            tools=[]
        )

    async def on_enter(self) -> None:
        """Called when agent becomes active"""
        userdata: UserData = self.session.userdata
        count = userdata.login_attempts
        userdata.login_attempts += 1

        push_status(f"screen: guard")

        self.logger.info(f"🎭 Entering {self.__class__.__name__} [{count}]")
        push_status(f"on_enter: {self.__class__.__name__} [{count}]")
        chat_ctx = self.chat_ctx.copy()

        # Add system instructions including user data context
        chat_ctx.add_message(
            role="system",
            content=f"You are guard agent in Alfred voice assistant. "
        )

        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply(tool_choice="none")

    async def _transfer_to_agent(self, name: str, context: RunContext_T, message: Optional[str] = None) -> tuple[Agent, str]:
        """Transfer to another agent"""
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.agents[name]
        userdata.prev_agent = current_agent

        self.logger.info(f"🔄 Transferring from {current_agent.__class__.__name__} to {name}")
        push_status(f"transfer_to_agent: {current_agent.__class__.__name__} to {name}")

        return next_agent, message or f"Transferring to {name} agent."

    @function_tool()
    async def check_password(self, password: Annotated[str, "The password to check in lowercase"], context: RunContext_T) -> tuple[Agent, str]:
        self.logger.info(f"Checking password [{count}] attempt: {password}")

        """Called when user wants to enter the house"""
        userdata: UserData = self.session.userdata
        if not password:
            return await self._transfer_to_agent("guard", context, "Incorrect password")

        password = password.lower()
        user_password = userdata.user_password.lower() if userdata.user_password else None

        if password == user_password:
            push_status(f"check_password -> correct")
            return await self._transfer_to_agent("alfred", context, "Correct password. Welcome home Bruce Wayne...")
        else:
            push_status(f"check_password -> incorrect")
            return await self._transfer_to_agent("guard", context, "Incorrect password")

    async def close_session(self):
        """Called when user want to leave the conversation"""

        self.logger.info("Closing session from function tool")
        await self.session.generate_reply(instructions="Goodbye Bruce Wayne")

        await asyncio.sleep(2)

        # don't await it, the function call will be awaited before closing
        self._closing_task = asyncio.create_task(self.session.aclose())
