

from typing import Any, Optional
from dataclasses import dataclass

from . import erroring

Identifier = int | str
Parameters = None | list | dict


@dataclass
class QueryMessage:
    method: str
    params: Parameters
    id: Identifier


@dataclass
class NotificationMessage:
    method: str
    params: Parameters


@dataclass
class ErrorMessage:
    error: erroring.JsonRpcError
    id: Optional[Identifier] = None


@dataclass
class ResultMessage:
    result: Any
    id: Identifier


Message = QueryMessage | NotificationMessage | ErrorMessage | ResultMessage


@dataclass
class IncomingError:
    error: erroring.JsonRpcError
    id: Optional[Identifier] = None
