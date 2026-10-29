"""Windows: helper subprocesses must not open a visible console window."""
import subprocess
import unittest
from unittest import mock

import process

NO_WINDOW = 0x08000000
NEW_GROUP = 0x00000200


class TestNoConsoleWindow(unittest.TestCase):
    def test_windows_worker_flags_include_no_window_and_new_group(self):
        with mock.patch.object(process.os, "name", "nt"):
            flags = process._own_process_group()["creationflags"]
        self.assertTrue(flags & NO_WINDOW)
        self.assertTrue(flags & NEW_GROUP)

    def test_windows_no_window_helper(self):
        with mock.patch.object(process.os, "name", "nt"):
            self.assertEqual(process._no_window(), {"creationflags": NO_WINDOW})

    def test_posix_unchanged(self):
        with mock.patch.object(process.os, "name", "posix"):
            self.assertEqual(process._no_window(), {})
            self.assertEqual(process._own_process_group(), {"start_new_session": True})

    def test_cmdkey_probe_passes_no_window(self):
        calls = []

        def fake_run(*a, **kw):
            calls.append(kw)
            return subprocess.CompletedProcess(a, 0, stdout=b"gemini:antigravity", stderr=b"")

        with mock.patch.object(process.os, "name", "nt"), mock.patch.object(process.subprocess, "run", fake_run):
            self.assertTrue(process._windows_credential_present())
        self.assertEqual(calls[0].get("creationflags"), NO_WINDOW)


if __name__ == "__main__":
    unittest.main()
