

import asyncio
import time

from jsonprcmisc.agent import Agent
from jsonprcmisc.backend_tcp_lines import cancelling, consume
from jsonprcmisc.backend_tcp_lines import build_agent


class Dispatcher:
    async def time(self):
        return time.time()


#async def handle_tcp_jsonrpc2(reader, writer):
#    async with asyncio.TaskGroup() as tg:
#        async def send(string):
#            print("Sending %r" % string)
#            writer.write(string.encode("ascii"))
#            writer.write(b"\n")
#        agent = Agent(tg, send, Dispatcher())
#        async with cancelling(tg.create_task(consume(agent, reader))):
#            await agent.serve_forever()


async def handle_tcp_jsonrpc(reader, writer):
    async with build_agent(Dispatcher(), reader, writer) as agent:
        await agent.serve_forever()


async def main():
    server = await asyncio.start_server(handle_tcp_jsonrpc, "127.0.0.1", 1234)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
