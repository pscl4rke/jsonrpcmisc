

from dataclasses import dataclass
from typing import Callable, List, Tuple

import asyncio
import inspect

from . import erroring
from . import formatting
from . import modelling
from . import parsing


# FIXME TOTAL MESS


def params_to_args_or_kwargs(params: modelling.Parameters) -> Tuple[tuple, dict]:
    if params is None:
        return tuple(), dict()
    if isinstance(params, list):
        return tuple(params), dict()
    if isinstance(params, dict):
        return tuple(), params
    raise NotImplementedError(str(type(params)))


@dataclass
class Agent:
    taskgroup: asyncio.TaskGroup
    send: Callable  # this needs to be an async callable FIXME
    dispatcher: object

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
            # run but throw away the response
            # FIXME this needs to be run in a task somehow?!?!
            run_method_until_response(parsed.id, parsed.method, parsed.params)
        if isinstance(parsed, modelling.QueryMessage):
            pass
        if isinstance(parsed, modelling.ResultMessage):
            pass
        if isinstance(parsed, modelling.ErrorMessage):
            pass

    async def run_method_until_response(self, id: modelling.Identifier, method_name: str,
                                        params: modelling.Parameters) -> modelling.Message:
        # FIXME ensure there is no underscore prefix
        try:
            method = getattr(self.dispatcher, method_name)
        except AttributeError:
            return modelling.ErrorMessage(error=erroring.ERROR_METHOD_NOT_FOUND, id=id)
        # FIXME check that it is an awaitable function
        args, kwargs = params_to_args_or_kwargs(params)
        try:
            inspect.signature(method).bind(*args, **kwargs)
        except TypeError:
            return modelling.ErrorMessage(error=erroring.ERROR_INVALID_PARAMS, id=id)
        try:
            result = await method(*args, **kwargs)
            return modelling.ResultMessage(result=result, id=id)
        except Exception:
            # FIXME what are we doing about logging, esp tracebacks?
            return modelling.ErrorMessage(error=erroring.ERROR_CATCH_ALL, id=id)
