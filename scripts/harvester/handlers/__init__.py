"""Handler registry for follow-news harvester."""

from typing import Callable

HANDLERS: dict[str, Callable] = {}


def register(source_type: str):
    """Decorator to register a handler function for a source type."""
    def decorator(fn):
        HANDLERS[source_type] = fn
        return fn
    return decorator


def get_handler(source_type: str):
    """Get a handler by source type name."""
    return HANDLERS.get(source_type)


def list_types() -> list[str]:
    """List all registered source types."""
    return list(HANDLERS.keys())
