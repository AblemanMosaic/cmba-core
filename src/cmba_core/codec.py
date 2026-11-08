"""CMBA-CJSON-I1: finite canonical JSON, not RFC 8785 / JCS.

The admitted value grammar follows the overlapping DKN candidate JSON grammar,
but resource ceilings and refusal namespace are new and explicit. No DKN import.
"""
from __future__ import annotations
import json
from typing import Any
from .errors import Refusal, require

MAX_BYTES = 1024 * 1024
MAX_DEPTH = 32
MAX_ITEMS = 1024
MAX_NODES = 16384
MAX_STRING_BYTES = 256 * 1024
CODEC = 'cmba-cjson-i1'


def _validate(value: Any, depth: int, budget: list[int]) -> None:
    require(depth <= MAX_DEPTH, 'CMBA_DEPTH_LIMIT')
    budget[0] += 1
    require(budget[0] <= MAX_NODES, 'CMBA_NODE_LIMIT')
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        require(-(2**63) <= value < 2**63, 'CMBA_INTEGER_RANGE')
        return
    if type(value) is str:
        require(len(value) <= MAX_STRING_BYTES, 'CMBA_STRING_LIMIT')
        require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), 'CMBA_STRING_INVALID')
        size = len(value.encode('utf-8'))
        require(size <= MAX_STRING_BYTES, 'CMBA_STRING_LIMIT')
        budget[1] += size
        require(budget[1] <= MAX_BYTES, 'CMBA_BYTE_LIMIT')
        return
    if type(value) is list:
        require(len(value) <= MAX_ITEMS, 'CMBA_COLLECTION_LIMIT')
        for item in value:
            _validate(item, depth + 1, budget)
        return
    if type(value) is dict:
        require(len(value) <= MAX_ITEMS, 'CMBA_COLLECTION_LIMIT')
        for key, item in value.items():
            require(type(key) is str, 'CMBA_OBJECT_KEY')
            _validate(key, depth + 1, budget)
            _validate(item, depth + 1, budget)
        return
    raise Refusal('CMBA_VALUE_TYPE')


def canonical(value: Any) -> bytes:
    _validate(value, 0, [0, 0])
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    require(len(raw) <= MAX_BYTES, 'CMBA_BYTE_LIMIT')
    return raw


def _depth_scan(raw: bytes) -> None:
    """Preflight nesting before the JSON decoder allocates nested structures."""
    quoted = escaped = False
    depth = 0
    for b in raw:
        if quoted:
            if escaped:
                escaped = False
            elif b == 92:
                escaped = True
            elif b == 34:
                quoted = False
        elif b == 34:
            quoted = True
        elif b in (91, 123):
            depth += 1
            require(depth <= MAX_DEPTH + 1, 'CMBA_DEPTH_LIMIT')
        elif b in (93, 125):
            depth -= 1
            require(depth >= 0, 'CMBA_JSON_INVALID')


def decode(raw: bytes, *, canonical_required: bool = True) -> Any:
    """Noncanonical decoding is an explicit authoring/CHC input operation only."""
    require(type(raw) is bytes, 'CMBA_BYTES_REQUIRED')
    require(type(canonical_required) is bool, 'CMBA_ARGUMENT_TYPE')
    require(len(raw) <= MAX_BYTES, 'CMBA_BYTE_LIMIT')
    _depth_scan(raw)
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'CMBA_DUPLICATE_KEY')
            result[key] = value
        return result
    def invalid_number(_):
        raise Refusal('CMBA_NUMBER_INVALID')
    try:
        result = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                            parse_float=invalid_number, parse_constant=invalid_number)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Refusal('CMBA_JSON_INVALID') from exc
    encoded = canonical(result)
    if canonical_required:
        require(encoded == raw, 'CMBA_NOT_CANONICAL')
    return result


def clone(value: Any) -> Any:
    return decode(canonical(value))
