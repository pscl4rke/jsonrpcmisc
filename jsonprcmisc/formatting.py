

from typing import Any, Dict

import json

from . import modelling


def format_response(response: modelling.Response) -> str:
    if isinstance(response, modelling.ResultResponse):
        return json.dumps(fields_for_result_response(response))
    elif isinstance(response, modelling.ErrorResponse):
        return json.dumps(fields_for_error_response(response))
    else:
        raise NotImplementedError(str(type(response)))


def fields_for_result_response(response: modelling.ResultResponse) -> Dict[str, Any]:
    fields: Dict[str, Any] = {"jsonrpc": "2.0"}
    fields["result"] = response.result
    fields["id"] = response.id
    return fields


def fields_for_error_response(response: modelling.ErrorResponse) -> Dict[str, Any]:
    fields: Dict[str, Any] = {"jsonrpc": "2.0"}
    fields["error"] = fields_for_error(response.error)
    if response.id is not None:
        fields["id"] = response.id
    return fields


def fields_for_error(error: modelling.JsonRpcError) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}
    fields["code"] = error.code
    fields["message"] = error.message
    if error.data is not None:
        fields["data"] = error.data
    return fields
