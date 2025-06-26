

from typing import Any, Dict, List

import json

from . import erroring
from . import modelling


def format_message(message: modelling.Message) -> str:
    return json.dumps(fields_for_message(message))


def format_batch(batch: List[modelling.Message]) -> str:
    return json.dumps([
        fields_for_message(message)
        for message in batch
    ])


def fields_for_message(message: modelling.Message) -> Dict[str, Any]:
    if isinstance(message, modelling.QueryMessage):
        return fields_for_query_message(message)
    if isinstance(message, modelling.NotificationMessage):
        return fields_for_notfication_message(message)
    if isinstance(message, modelling.ResultMessage):
        return fields_for_result_message(message)
    if isinstance(message, modelling.ErrorMessage):
        return fields_for_error_message(message)
    raise NotImplementedError(str(type(message)))


def fields_for_query_message(message: modelling.QueryMessage) -> Dict[str, Any]:
    fields: Dict[str, Any] = {"jsonrpc": "2.0"}
    fields["method"] = message.method
    if message.params is not None:
        fields["params"] = message.params
    fields["id"] = message.id
    return fields


def fields_for_notfication_message(message: modelling.NotificationMessage) -> Dict[str, Any]:
    fields: Dict[str, Any] = {"jsonrpc": "2.0"}
    fields["method"] = message.method
    if message.params is not None:
        fields["params"] = message.params
    return fields


def fields_for_result_message(message: modelling.ResultMessage) -> Dict[str, Any]:
    fields: Dict[str, Any] = {"jsonrpc": "2.0"}
    fields["result"] = message.result
    fields["id"] = message.id
    return fields


def fields_for_error_message(message: modelling.ErrorMessage) -> Dict[str, Any]:
    fields: Dict[str, Any] = {"jsonrpc": "2.0"}
    fields["error"] = fields_for_error(message.error)
    if message.id is not None:
        fields["id"] = message.id
    return fields


def fields_for_error(error: erroring.JsonRpcError) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}
    fields["code"] = error.code
    fields["message"] = error.message
    if error.data is not None:
        fields["data"] = error.data
    return fields
