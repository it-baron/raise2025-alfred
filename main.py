#!/usr/bin/env python3
"""
Alfred Voice Worker - Central Voice Assistant
Brings together all Alfred agents in a single LiveKit session
Following clean architecture patterns from EXAMPLE_PY.md
"""

import os
import asyncio
import logging
import urllib.parse
from dotenv import load_dotenv
import functools

# Add agents directory to path

# Now import your agents
from agents.base_agent import UserData, get_llm_instance, voices
from agents.greeter.main import GreeterA
from agents.planner.main import PlannerA
from agents.gmail.main import GMailA
from agents.gcal.main import GCalA
from agents.gtasks.main import GTasksA

from livekit.agents import JobContext, WorkerOptions, cli, mcp
from livekit.agents.voice import AgentSession
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import silero, groq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alfred-voice-worker")

# Load environment variables from .env.local
load_dotenv(".env.local")

# --- Monkey patch for prepare_function_arguments to fix NoneType error ---
import livekit.agents.llm.utils as llm_utils

def patched_prepare_function_arguments(*, fnc, json_arguments, call_ctx=None):
    """
    Monkey-patched version of prepare_function_arguments to handle NoneType args_dict.
    """
    import inspect
    from typing import get_type_hints
    from pydantic_core import from_json
    from livekit.agents.llm.utils import (
        is_function_tool, is_raw_function_tool, function_arguments_to_pydantic_model, _is_optional_type, _shallow_model_dump, is_context_type
    )

    signature = inspect.signature(fnc)
    type_hints = get_type_hints(fnc, include_extras=True)
    args_dict = from_json(json_arguments)

    # Patch: If args_dict is None, treat as empty dict
    if args_dict is None:
        args_dict = {}

    if is_function_tool(fnc):
        model_type = function_arguments_to_pydantic_model(fnc)
        for param_name, param in signature.parameters.items():
            type_hint = type_hints[param_name]
            if param_name in args_dict and args_dict[param_name] is None:
                if not _is_optional_type(type_hint):
                    if param.default is not inspect.Parameter.empty:
                        args_dict[param_name] = param.default
                    else:
                        raise ValueError(
                            f"Received None for required parameter '{param_name} ;"
                            "this argument cannot be None and no default is available."
                        )
        model = model_type.model_validate(args_dict)
        raw_fields = _shallow_model_dump(model)
    elif is_raw_function_tool(fnc):
        raw_fields = {"raw_arguments": args_dict}
    else:
        raise ValueError(f"Unsupported function tool type: {type(fnc)}")

    context_dict = {}
    for param_name, _ in signature.parameters.items():
        type_hint = type_hints[param_name]
        if is_context_type(type_hint) and call_ctx is not None:
            context_dict[param_name] = call_ctx

    bound = signature.bind(**{**raw_fields, **context_dict})
    bound.apply_defaults()
    return bound.args, bound.kwargs

llm_utils.prepare_function_arguments = patched_prepare_function_arguments
# --- End monkey patch ---

async def entrypoint(ctx: JobContext):
    """Main entrypoint for Alfred voice assistant"""
    await ctx.connect()

    logger.info("🦇 Alfred Voice Assistant starting...")

    # MCP Server configuration for external communication
    base_url = os.getenv("CORAL_SSE_URL", "http://localhost:5555/devmode/alfred-assistant/privkey/alfred-session1/sse")
    params = {
        "agentId": os.getenv("CORAL_AGENT_ID", "alfred-assistant"),
        "agentDescription": "Alfred Pennyworth voice assistant for Master Bruce Wayne - handles email, calendar, and task management"
    }
    query_string = urllib.parse.urlencode(params)
    MCP_SERVER_URL = f"{base_url}?{query_string}"

    logger.info(f"🐚 MCP Server URL: {MCP_SERVER_URL}")

    # Initialize user data
    userdata = UserData()

    # Create all Alfred agents
    userdata.agents.update({
        "greeter": GreeterA(),
        "planner": PlannerA(),
        "gmail": GMailA(),
        "calendar": GCalA(),
        "gtasks": GTasksA(),
    })

    logger.info("🎭 All Alfred agents initialized:")
    for agent_name in userdata.agents.keys():
        logger.info(f"  - {agent_name}")

    # Create agent session
    session = AgentSession[UserData](
        userdata=userdata,
        stt=groq.STT(model=os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")),
        llm=get_llm_instance(),
        tts=groq.TTS(voice=os.getenv("GROQ_TTS_VOICE", "Arista-PlayAI"), model=os.getenv("GROQ_TTS_MODEL", "playai-tts")),  # Each agent will use its own Groq TTS
        vad=silero.VAD.load(),
        max_tool_steps=5,
        mcp_servers=[
            mcp.MCPServerHTTP(
                url=MCP_SERVER_URL,
                timeout=100,
                client_session_timeout_seconds=100,
            ),
        ]
    )

    logger.info("🎤 Starting voice session with Alfred (Greeter agent)")

    # Start with the Greeter agent (Alfred)
    await session.start(
        agent=userdata.agents["greeter"],
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )

    logger.info("✅ Alfred Voice Assistant ready for Master Bruce")

if __name__ == "__main__":
    logger.info("🦇 Alfred Voice Worker initializing...")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))