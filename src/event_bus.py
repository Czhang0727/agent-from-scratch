#!/usr/bin/env python3
"""
Event Bus Module - A simple publish/subscribe event system.
"""

import threading
from collections import defaultdict
from typing import Callable, Any


class EventBus:
    """
    A simple pub/sub event bus.
    Publishers emit named events, subscribers receive them via callbacks.
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event: str, callback: Callable[..., Any]) -> None:
        """Subscribe a callback to a named event."""
        with self._lock:
            self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable[..., Any]) -> None:
        """Remove a callback from a named event."""
        with self._lock:
            self._subscribers[event].remove(callback)

    def publish(self, event: str, *args, **kwargs) -> None:
        """Publish an event, calling all subscribers synchronously."""
        with self._lock:
            callbacks = list(self._subscribers[event])
        for callback in callbacks:
            callback(*args, **kwargs)
