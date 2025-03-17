from typing import Any

from starlette.requests import Request


def set_context(request: Request, key: str, value: Any):
    setattr(request.state, key, value)


def get_context(request: Request, key: str) -> Any:
    value = getattr(request.state, key, None)
    # request.scope["state"][key] = value
    return value
