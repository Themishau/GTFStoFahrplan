import unittest
from threading import RLock
from unittest.mock import patch

from model.infrastructure import python_runtime


class PythonRuntimeCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_applied = python_runtime._threading_shutdown_fix_applied
        python_runtime._threading_shutdown_fix_applied = False

    def tearDown(self) -> None:
        python_runtime._threading_shutdown_fix_applied = self.original_applied

    def test_python_313_fix_keeps_finalizer_dependencies_alive(self) -> None:
        class DummyThreadCleanup:
            def __del__(self) -> None:
                pass

        active_threads = {}
        active_threads_lock = RLock()
        with (
            patch.object(
                python_runtime.threading,
                "_DeleteDummyThreadOnDel",
                DummyThreadCleanup,
                create=True,
            ),
            patch.object(
                python_runtime.threading,
                "_active",
                active_threads,
                create=True,
            ),
            patch.object(
                python_runtime.threading,
                "_active_limbo_lock",
                active_threads_lock,
                create=True,
            ),
            patch.object(python_runtime.sys, "version_info", (3, 13, 3)),
        ):
            self.assertTrue(
                python_runtime.apply_python_313_threading_shutdown_fix()
            )
            self.assertFalse(
                python_runtime.apply_python_313_threading_shutdown_fix()
            )

        defaults = DummyThreadCleanup.__del__.__defaults__
        if defaults is None:
            self.fail("Compatibility finalizer did not capture its dependencies")
        self.assertIs(defaults[0], active_threads_lock)
        self.assertIs(defaults[1], active_threads)

    def test_fixed_python_version_does_not_modify_threading(self) -> None:
        class DummyThreadCleanup:
            def __del__(self) -> None:
                pass

        original_cleanup = DummyThreadCleanup.__del__
        with (
            patch.object(
                python_runtime.threading,
                "_DeleteDummyThreadOnDel",
                DummyThreadCleanup,
                create=True,
            ),
            patch.object(python_runtime.sys, "version_info", (3, 13, 6)),
        ):
            self.assertFalse(
                python_runtime.apply_python_313_threading_shutdown_fix()
            )

        self.assertIs(DummyThreadCleanup.__del__, original_cleanup)


if __name__ == "__main__":
    unittest.main()
