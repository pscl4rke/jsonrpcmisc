

from dataclasses import dataclass
from typing import Callable, List

import asyncio

from . import formatting
from . import modelling
from . import parsing


# FIXME TOTAL MESS


@dataclass
class Agent:
    taskgroup: asyncio.TaskGroup
    send: Callable  # this needs to be an async callable FIXME

    async def inject_received_message(self, message: str | bytes) -> None:
        parsed = parsing.parse_incoming(message)
        if isinstance(parsed, list):  # batch
            self.taskgroup.create_task(self.react_to_batch(parsed))
            #self.react_to_batch(parsed)
        else:
            #self.taskgroup.create_task(self.react_to_single(parsed))
            await self.react_to_single(parsed)

    async def react_to_batch(self, batch: List[parsing.Parsed]) -> None:
        responses: List[modelling.Message] = []
        #async with asyncio.TaskGroup() as batch_taskgroup:
        #    for request in batch:
        #        if isinstance(request, modelling.ErrorMessage):
        #            responses.append(request)
        #        elif isinstance(request, modelling.QueryMessage):
        #            FIXME
        #        elif isinstance(request, modelling.NotificationMessage):
        #            FIXME
        #        else:
        #            raise NotImplementedError(repr(request))
        if len(responses) > 0:
            await self.send(formatting.format_batch(responses))

    async def react_to_single(self, parsed):
        if isinstance(parsed, modelling.IncomingError):
            await self.send(formatting.format_message(modelling.ErrorMessage(
                error=parsed.error,
                id=parsed.id,
            )))
        if isinstance(parsed, modelling.NotificationMessage):
            pass
        if isinstance(parsed, modelling.QueryMessage):
            pass
        if isinstance(parsed, modelling.ResultMessage):
            pass
        if isinstance(parsed, modelling.ErrorMessage):
            pass
