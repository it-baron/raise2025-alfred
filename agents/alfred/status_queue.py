import janus
import asyncio

_status_queue = None


def init(loop: asyncio.AbstractEventLoop | None = None) -> None:
    """
    Call once from the *async* thread (FastAPI lifespan) to create the queue.
    """
    global _status_queue
    if _status_queue is None:
        if loop is None:                      # default: current running loop
            loop = asyncio.get_running_loop()
        _status_queue = janus.Queue()

# Shared status queue for SSE (sync/async bridge)
def get_status_queue() -> janus.Queue:
    if _status_queue is None:
        raise ValueError("Status queue not initialized")
    return _status_queue

def push_status(msg: str) -> None:
    status_queue = get_status_queue()
    print(f"push_status [{id(status_queue)}]", msg, flush=True)
    """Thread-safe push to the status queue from any thread (sync)."""
    status_queue.sync_q.put(msg)

async def push_status_async(msg: str) -> None:
    status_queue = get_status_queue()
    """Async push to the status queue from async code."""
    print(f"push_status_async [{id(status_queue)}]", msg, flush=True)
    await status_queue.async_q.put(msg)

