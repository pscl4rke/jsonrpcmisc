

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

import asyncio
import inspect

from . import erroring
from . import formatting
from . import modelling
from . import parsing


# Note that JSON-RPC really has no way to specify that things
# (esp notifications) are processed in order.  So you can't rely
# on this for queueing things up.


# Also note that the whole batching concept feels very impractical,
# and will inevitably not work that well.  This implementation is
# NOT spec-compliant because it happily receives a batch, but then
# handles everything inside in isolation and responds to each one
# individually.


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
    _last_id: int = 0
    _pending: Dict[int, asyncio.Future] = field(default_factory=lambda: {})

    async def inject_received_message(self, message: str | bytes) -> None:
        parsed = parsing.parse_incoming(message)
        if isinstance(parsed, list):  # batch
            #self.taskgroup.create_task(self.react_to_batch(parsed))
            for request in parsed:
                self.taskgroup.create_task(self.react_to_single(parsed))
        else:
            self.taskgroup.create_task(self.react_to_single(parsed))

    #async def react_to_batch(self, batch: List[parsing.Parsed]) -> None:
    #    responses: List[modelling.Message] = []
    #    async with asyncio.TaskGroup() as batch_taskgroup:
    #        for request in batch:
    #            if isinstance(request, modelling.ErrorMessage):
    #                if request.id in self._pending:
    #                    exc = erroring.Fault(repr(request.error))
    #                    self._pending[request.id].set_exception(exc)
    #            elif isinstance(request, modelling.ResultMessage):
    #                if request.id in self._pending:
    #                    self._pending[request.id].set_result(request.result)
    #            elif isinstance(request, modelling.QueryMessage):
    #                pass  # FIXME
    #            elif isinstance(request, modelling.NotificationMessage):
    #                # run but throw away the response
    #                batch_taskgroup.create_task(self.run_method_until_response(
    #                    request.id, request.method, request.params))
    #            else:
    #                raise NotImplementedError(repr(request))
    #    if len(responses) > 0:
    #        await self.send(formatting.format_batch(responses))

    async def react_to_single(self, parsed):
        if isinstance(parsed, modelling.IncomingError):
            await self.send(formatting.format_message(modelling.ErrorMessage(
                error=parsed.error,
                id=parsed.id,
            )))
        if isinstance(parsed, modelling.NotificationMessage):
            # run but throw away the response
            await self.run_method_until_response(parsed.id, parsed.method, parsed.params)
        if isinstance(parsed, modelling.QueryMessage):
            response = await self.run_method_until_response(parsed.id, parsed.method, parsed.params)
            await self.send(formatting.format_message(response))
        if isinstance(parsed, modelling.ResultMessage):
            if parsed.id in self._pending:
                self._pending[parsed.id].set_result(parsed.result)
        if isinstance(parsed, modelling.ErrorMessage):
            if parsed.id in self._pending:
                exc = erroring.Fault(repr(parsed.error))
                self._pending[parsed.id].set_exception(exc)

    async def run_method_until_response(self, id: modelling.Identifier, method_name: str,
                                        params: modelling.Parameters) -> modelling.Message:
        if method_name.startswith("_"):  # underscore hides methods
            return modelling.ErrorMessage(error=erroring.ERROR_METHOD_NOT_FOUND, id=id)
        try:
            method = getattr(self.dispatcher, method_name)
        except AttributeError:
            return modelling.ErrorMessage(error=erroring.ERROR_METHOD_NOT_FOUND, id=id)
        if not inspect.iscoroutinefunction(method):
            return modelling.ErrorMessage(error=erroring.ERROR_METHOD_NOT_FOUND, id=id)
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

    def generate_id(self) -> int:
        self._last_id += 1
        return self._last_id

    async def call(self, method_name: str, params: modelling.Parameters,
                   timeout: float = 10) -> Any:
        id = self.generate_id()
        future: asyncio.Future = asyncio.Future()
        self._pending[id] = future
        try:
            await self.send(formatting.format_message(modelling.QueryMessage(
                method_name, params, id)))
            async with asyncio.timeout(timeout):
                await future
            return future.result()
        finally:
            del self._pending[id]

    async def serve_forever(self):
        await asyncio.Future()
