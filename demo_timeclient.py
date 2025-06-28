

import asyncio

from jsonprcmisc.agent import Agent
from jsonprcmisc.backend_tcp_lines import cancelling, consume
from jsonprcmisc.backend_tcp_lines import build_agent


#async def main2():
#    async with asyncio.TaskGroup() as tg:
#        reader, writer = await asyncio.open_connection("127.0.0.1", 1234)
#        async def send(string):
#            print("Sending %r" % string)
#            writer.write(string.encode("ascii"))
#            writer.write(b"\n")
#        agent = Agent(tg, send, object())
#        async with cancelling(tg.create_task(consume(agent, reader))):
#            print(await agent.call("time", None, 3))
#            await asyncio.sleep(1)
#            print(await agent.call("time", None, 3))


async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 1234)
    async with build_agent(object(), reader, writer) as agent:
        print(await agent.call("time", None, 3))
        await asyncio.sleep(1)
        print(await agent.call("time", None, 3))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
