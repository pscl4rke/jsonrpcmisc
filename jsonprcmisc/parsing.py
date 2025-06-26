

from typing import List

import logging
LOG = logging.getLogger(__name__)

import json

from . import modelling


Parsed = modelling.QueryRequest | modelling.NotificationRequest | modelling.ErrorResponse


def parse_message(message: str | bytes) -> Parsed | List[Parsed]:
    try:
        doc = json.loads(message)
    except json.JSONDecodeError as exc:
        LOG.debug("JSON error: %r", exc)
        return modelling.ErrorResponse(modelling.ERROR_PARSE)
    if isinstance(doc, list):  # a batch
        return [decode_incoming(x) for x in doc]
    return decode_incoming(doc)


def decode_incoming(doc: dict) -> Parsed:
    # Be very forgiving if receiving errors from the other side:
    if "error" in doc:
        return modelling.ErrorResponse(
            error=modelling.JsonRpcError(
                code=doc.get("error", {}).get("code", -32603),
                message=doc.get("error", {}).get("message", "(no message)"),
                data=doc.get("error", {}).get("data", None),
            ),
            id=doc.get("id", None),
        )
    id = None
    try:
        assert doc["jsonrpc"] == "2.0"
        if "id" in doc:
            id = doc["id"]
            return modelling.QueryRequest(
                method=doc["method"],
                params=doc.get("params", None),
                id=id,
            )
        else:
            return modelling.NotificationRequest(
                method=doc["method"],
                params=doc.get("params", None),
            )
    except Exception as exc:
        LOG.debug("Invalid: %r", exc)
        return modelling.ErrorResponse(modelling.ERROR_INVALID, id=id)
