

from typing import List

import logging
LOG = logging.getLogger(__name__)

import json

from . import erroring
from . import modelling


Parsed = modelling.Message | modelling.IncomingError


def parse_incoming(message: str | bytes) -> Parsed | List[Parsed]:
    try:
        doc = json.loads(message)
    except json.JSONDecodeError as exc:
        LOG.debug("JSON error: %r", exc)
        return modelling.IncomingError(erroring.ERROR_PARSE)
    if isinstance(doc, list):  # a batch
        return [decode_incoming_message(x) for x in doc]
    return decode_incoming_message(doc)


def decode_incoming_message(doc: dict) -> Parsed:
    # Be very forgiving if receiving errors from the other side:
    #   (we want to avoid a loop of firing an error back-and-to)
    if "error" in doc:
        return modelling.ErrorMessage(
            error=erroring.JsonRpcError(
                code=doc.get("error", {}).get("code", -32603),
                message=doc.get("error", {}).get("message", "(no message)"),
                data=doc.get("error", {}).get("data", None),
            ),
            id=doc.get("id", None),
        )
    try:
        assert doc["jsonrpc"] == "2.0"
        if "id" not in doc:
            return modelling.NotificationMessage(
                method=doc["method"],
                params=doc.get("params", None),
            )
        elif "method" in doc:
            return modelling.QueryMessage(
                method=doc["method"],
                params=doc.get("params", None),
                id=doc["id"],
            )
        else:
            return modelling.ResultMessage(
                result=doc["result"],
                id=doc["id"],
            )
    except Exception as exc:
        LOG.debug("Invalid: %r", exc)
        return modelling.IncomingError(erroring.ERROR_INVALID, id=doc.get("id"))
