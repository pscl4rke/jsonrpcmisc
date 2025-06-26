

from typing import List

import logging
LOG = logging.getLogger(__name__)

import json

from . import models


Parsed = models.QueryRequest | models.NotificationRequest | models.ErrorResponse


def parse_message(message: str | bytes) -> Parsed | List[Parsed]:
    try:
        doc = json.loads(message)
    except json.JSONDecodeError as exc:
        LOG.debug("JSON error: %r", exc)
        return models.ErrorResponse(models.ERROR_PARSE)
    if isinstance(doc, list):  # a batch
        return [decode_request(x) for x in doc]
    return decode_request(doc)


def decode_request(doc: dict) -> Parsed:
    id = None
    try:
        assert doc["jsonrpc"] == "2.0"
        if "id" in doc:
            id = doc["id"]
            return models.QueryRequest(
                method=doc["method"],
                params=doc.get("params", None),
                id=id,
            )
        else:
            return models.NotificationRequest(
                method=doc["method"],
                params=doc.get("params", None),
            )
    except Exception as exc:
        LOG.debug("Invalid: %r", exc)
        return models.ErrorResponse(models.ERROR_INVALID, id=id)
