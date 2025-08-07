from typing import Any


def clear_globals(gb: dict[str, Any]):
    return {k: gb[k] for k in gb if k not in ("__builtins__", "__cached__")}
