

from contextlib import asynccontextmanager

import asyncio

from jsonprcmisc.agent import Agent


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


@asynccontextmanager
async def build_agent(dispatcher, reader, writer):
    async with asyncio.TaskGroup() as tg:

        async def send(string):
            text = string.encode("ascii") + b"\n"
            print("Sending %r" % text)
            writer.write(text)

        agent = Agent(tg, send, dispatcher)
        async with cancelling(tg.create_task(consume(agent, reader))):
            yield agent
