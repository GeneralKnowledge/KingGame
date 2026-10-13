from __future__ import annotations

import itertools

_counter = itertools.count(1)


def reset_id_counter(start: int = 1) -> None:
    global _counter
    _counter = itertools.count(start)


def new_id(prefix: str) -> str:
    return f"{prefix}_{next(_counter)}"
