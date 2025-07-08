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
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn
import threading
from status_queue import push_status, init as init_status_queue, get_status_queue, push_status_async
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import queue
from threading import Thread

# Add agents directory to path

# Now import your agents
from base_agent import UserData, get_llm_instance
from alfred import AlfredA
from guard import GuardA
from livekit.agents import JobContext, WorkerOptions, cli, mcp, Worker, JobProcess
from livekit.agents.voice import AgentSession
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import silero, groq
from livekit.agents.job import JobExecutorType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alfred-voice-worker")

# Load environment variables from .env.local
load_dotenv(".env.local")

# --- Monkey patch for prepare_function_arguments to fix NoneType error ---
import livekit.agents.llm.utils as llm_utils
from livekit.agents.llm.tool_context import is_function_tool, is_raw_function_tool

def patched_prepare_function_arguments(*, fnc, json_arguments, call_ctx=None):
    """
    Monkey-patched version of prepare_function_arguments to handle NoneType args_dict.
    """
    import inspect
    from typing import get_type_hints
    from pydantic_core import from_json
    from livekit.agents.llm.utils import (
        function_arguments_to_pydantic_model, _is_optional_type, _shallow_model_dump, is_context_type
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

# FastAPI app for SSE and static
@asynccontextmanager
async def lifespan(app):
    init_status_queue()
    await push_status_async("SSE is working")
    yield

app = FastAPI(lifespan=lifespan)
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/status/stream")
async def status_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            try:
                print(f"stream status_queue [{id(get_status_queue())}]", flush=True)
                msg = await get_status_queue().async_q.get()
                yield {"event": "status", "data": msg}
            except Exception as e:
                logger.error(f"Exception in status_stream event_generator: {e}")
                break
    return EventSourceResponse(event_generator())

@app.post("/status/push")
async def push_test_status(msg: str = Form(...)):
    await push_status_async(msg)
    return {"status": "ok"}

@app.get("/")
async def root():
    with open(os.path.join(static_dir, "index.html"), "r") as f:
        return HTMLResponse(f.read())


async def entrypoint(ctx: JobContext):
    """Main entrypoint for Alfred voice assistant"""
    await ctx.connect()

    logger.info("🦇 Alfred Voice Assistant starting...")
    push_status("Alfred Voice Assistant starting...")

    # MCP Server configuration for external communication
    base_url = os.getenv("CORAL_SSE_URL", "http://localhost:5555/devmode/alfred-assistant/privkey/alfred-session1/sse")
    params = {
        "agentId": os.getenv("CORAL_AGENT_ID", "alfred-assistant"),
        "agentDescription": "Alfred Pennyworth voice assistant for Master Bruce Wayne - handles email, calendar, and task management"
    }
    query_string = urllib.parse.urlencode(params)
    MCP_SERVER_URL = f"{base_url}?{query_string}"

    logger.info(f"🐚 MCP Server URL: {MCP_SERVER_URL}")
    push_status(f"MCP Server URL: {MCP_SERVER_URL}")

    # Initialize user data
    userdata = UserData()

    # Create all Alfred agents
    userdata.agents.update({
        "guard": GuardA(),
        "alfred": AlfredA()
    })

    logger.info("🎭 All Alfred agents initialized:")
    for agent_name in userdata.agents.keys():
        logger.info(f"  - {agent_name}")
        push_status(f"Agent initialized: {agent_name}")

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

    from livekit.agents.voice.events import UserInputTranscribedEvent, AgentStateChangedEvent, FunctionToolsExecutedEvent

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        logger.info(f"User input transcribed: {event.transcript}, final: {event.is_final}, speaker id: {event.speaker_id}")

    @session.on("agent_state_changed")
    def agent_state_changed(event: AgentStateChangedEvent):
        logger.info(f"Agent state changed: {event.old_state}, new state: {event.new_state}")
        push_status(f"Agent state changed: {event.old_state}, new state: {event.new_state}")

    @session.on("close")
    def on_close():
        logger.info("Session closed")
        push_status("screen: intro")

    @session.on("function_tools_executed")
    def on_function_tools_executed(event: FunctionToolsExecutedEvent):
        logger.info(f"Function tools executed: {event.function_calls[0].name}")
        push_status(f"tool: {event.function_calls[0].name}")

    logger.info("🎤 Starting voice session with Alfred (Guard agent)")
    push_status("Starting voice session with Alfred (Guard agent)")

    await session.start(
        agent=userdata.agents["guard"],
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )

    logger.info("✅ Alfred Voice Assistant ready for Master Bruce")
    push_status("Alfred Voice Assistant ready for Master Bruce")


def run_api():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        workers=1,
        reload=False,
        log_level="info",
    )

async def run_worker():
    # build the worker with *thread* executor (same PID, same queue)
    opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        job_executor_type=JobExecutorType.THREAD,
        num_idle_processes=0,
        ws_url           = os.environ["LIVEKIT_URL"],
        api_key          = os.environ["LIVEKIT_API_KEY"],
        api_secret       = os.environ["LIVEKIT_API_SECRET"],
    )
    print("LIVEKIT_URL", os.environ.get("LIVEKIT_URL"))
    worker = Worker(opts, register=True, loop=asyncio.get_running_loop())

    # emit a status line once the worker is actually registered
    @worker.once("worker_started")
    def _on_started():
        logger.info("🛠  LiveKit worker registered  PID=%s", os.getpid())

    # run & catch startup problems
    try:
        await worker.run()          # blocks until SIGINT/SIGTERM
    except Exception:
        logger.exception("❌ LiveKit worker crashed during startup")
        raise                      # let asyncio.run() exit with non-zero

if __name__ == "__main__":
    # set logger to debug
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.ERROR)

    # disable livekit logging
    logging.getLogger("livekit").setLevel(logging.ERROR)
    logging.getLogger("livekit.agents").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.ERROR)

    # disable http logging
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("aiohttp").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    logging.getLogger("openai._base_client").setLevel(logging.ERROR)

    logger.info("🦇 Alfred Voice Worker initializing...")

    threading.Thread(target=run_api, daemon=True).start()
    asyncio.run(run_worker())
