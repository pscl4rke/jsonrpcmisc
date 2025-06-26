

from typing import Any, Optional
from dataclasses import dataclass


Identifier = int | str
Parameters = None | list | dict


@dataclass
class QueryRequest:
    method: str
    params: Parameters
    id: Identifier


@dataclass
class NotificationRequest:
    method: str
    params: Parameters


@dataclass
class JsonRpcError:
    code: int
    message: str
    data: Optional[Any] = None


ERROR_PARSE = JsonRpcError(code=-32700, message="Parse Error")
ERROR_INVALID = JsonRpcError(code=-32600, message="Invalid Request")
ERROR_METHOD_NOT_FOUND = JsonRpcError(code=-32601, message="Method Not Found")
ERROR_INVALID_PARAMS = JsonRpcError(code=-32602, message="Invalid Params")
ERROR_INTERNAL_ERROR = JsonRpcError(code=-32603, message="Internal Error")


@dataclass
class ErrorResponse:
    error: JsonRpcError
    id: Optional[Identifier] = None


@dataclass
class ResultResponse:
    result: Any
    id: Identifier


Response = ErrorResponse | ResultResponse
