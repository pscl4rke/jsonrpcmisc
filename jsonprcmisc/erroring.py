

from typing import Any, Optional
from dataclasses import dataclass


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

# FIXME makes sense to have an actually raisable exception so that method
# implementations can specify their own messages and codes.
ERROR_CATCH_ALL = JsonRpcError(code=-1, message="Error running method")


# Raised when a local client call gets an error response from the server.
# Perhaps could be merged with above.
# FIXME need to handle code and message and optional data
class Fault(Exception):
    pass
