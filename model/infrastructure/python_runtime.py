"""Compatibility fixes for supported Python runtimes."""

from __future__ import annotations

import sys
import threading
from typing import Any

_threading_shutdown_fix_applied = False


def apply_python_313_threading_shutdown_fix() -> bool:
    """Backport CPython gh-130522 for Python 3.13.0 through 3.13.5.

    Those releases look up ``threading`` module globals from a finalizer after
    interpreter shutdown may already have cleared them. Keeping the lock and
    active-thread dictionary in default arguments is the fix used by CPython.
    """
    global _threading_shutdown_fix_applied

    if _threading_shutdown_fix_applied:
        return False
    if sys.implementation.name != "cpython":
        return False
    if not ((3, 13, 0) <= sys.version_info[:3] < (3, 13, 6)):
        return False

    cleanup_type = getattr(threading, "_DeleteDummyThreadOnDel", None)
    active_threads = getattr(threading, "_active", None)
    active_threads_lock = getattr(threading, "_active_limbo_lock", None)
    if (
            cleanup_type is None
            or not isinstance(active_threads, dict)
            or active_threads_lock is None
    ):
        return False

    # The shared dictionary must stay strongly referenced by the function.
    # noinspection PyDefaultArgument
    def delete_dummy_thread(
            cleanup: Any,
            lock: Any = active_threads_lock,
            threads: dict[int, Any] = active_threads,
    ) -> None:
        thread_id = getattr(cleanup, "_tident")
        dummy_thread = getattr(cleanup, "_dummy_thread")
        with lock:
            if threads.get(thread_id) is dummy_thread:
                threads.pop(thread_id, None)

    cleanup_type.__del__ = delete_dummy_thread
    _threading_shutdown_fix_applied = True
    return True
