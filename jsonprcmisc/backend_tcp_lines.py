
from contextlib import asynccontextmanager


@asynccontextmanager
async def cancelling(task):
    """Like contextlib.closing(...), but calls .cancel() instead."""
    try:
        yield task
    finally:
        task.cancel()


async def consume(agent, reader):
    async for line in reader:
        print("Received %r" % line)
        await agent.inject_received_message(line)
