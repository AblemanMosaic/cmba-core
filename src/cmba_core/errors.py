"""Stable refusal codes for the CMBA I1 engineering profile."""
class Refusal(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def require(condition: bool, code: str) -> None:
    if not condition:
        raise Refusal(code)
