"""Strict public-key admission for v0.2, ported from the inherited r002 checker.

Signature generation/verification remains in cryptography/OpenSSL. This module
rejects identity, non-canonical, off-curve and non-prime-subgroup public keys.
These are public-data checks, not constant-time private-key operations.
"""
from functools import lru_cache

_P = 2**255 - 19
_D = (-121665 * pow(121666, _P - 2, _P)) % _P
_SQRT_M1 = pow(2, (_P - 1) // 4, _P)
_L = 2**252 + 27742317777372353535851937790883648493
_IDENTITY = (0, 1)


def _decode_point(encoded: bytes) -> tuple[int, int] | None:
    if len(encoded) != 32:
        return None
    value = int.from_bytes(encoded, "little")
    sign = (value >> 255) & 1
    y = value & ((1 << 255) - 1)
    if y >= _P:
        return None
    y2 = y * y % _P
    denominator = (_D * y2 + 1) % _P
    if denominator == 0:
        return None
    x2 = (y2 - 1) * pow(denominator, _P - 2, _P) % _P
    x = pow(x2, (_P + 3) // 8, _P)
    if x * x % _P != x2:
        x = x * _SQRT_M1 % _P
    if x * x % _P != x2 or (x == 0 and sign):
        return None
    if x & 1 != sign:
        x = _P - x
    return x, y


def _add(first: tuple[int, int], second: tuple[int, int]) -> tuple[int, int]:
    x1, y1 = first
    x2, y2 = second
    product = _D * x1 * x2 * y1 * y2 % _P
    x3 = (x1 * y2 + y1 * x2) * pow(1 + product, _P - 2, _P) % _P
    y3 = (y1 * y2 + x1 * x2) * pow(1 - product, _P - 2, _P) % _P
    return x3, y3


def _scalar(point: tuple[int, int], scalar: int) -> tuple[int, int]:
    result = _IDENTITY
    addend = point
    while scalar:
        if scalar & 1:
            result = _add(result, addend)
        addend = _add(addend, addend)
        scalar >>= 1
    return result



@lru_cache(maxsize=512)
def admitted_public_key(raw: bytes) -> bool:
    point = _decode_point(raw)
    return point is not None and point != _IDENTITY and _scalar(point, _L) == _IDENTITY
