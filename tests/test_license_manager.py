import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.utils import license_manager as lm


class LicenseManagerTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        base = Path(self._tmpdir.name)
        self._orig_app_dir = lm._APP_DIR
        self._orig_license_file = lm._LICENSE_FILE
        self._orig_legacy_file = lm._LEGACY_LICENSE_FILE
        lm._APP_DIR = base
        lm._LICENSE_FILE = base / ".session.bin"
        lm._LEGACY_LICENSE_FILE = base / "license.dat"

    def tearDown(self):
        lm._APP_DIR = self._orig_app_dir
        lm._LICENSE_FILE = self._orig_license_file
        lm._LEGACY_LICENSE_FILE = self._orig_legacy_file
        self._tmpdir.cleanup()

    def test_saved_activation_is_bound_to_current_machine(self):
        key = lm.generate_key()

        with patch.object(lm, "_machine_fingerprint", return_value="machine-a"):
            lm.save_activation(key, "Alice")
            self.assertTrue(lm.is_activated())
            self.assertEqual(lm.get_username(), "Alice")

        with patch.object(lm, "_machine_fingerprint", return_value="machine-b"):
            self.assertFalse(lm.is_activated())
            self.assertEqual(lm.get_username(), "")
            self.assertEqual(lm.get_key(), "")

    def test_legacy_plain_key_is_still_accepted(self):
        key = lm.generate_key()
        lm._LEGACY_LICENSE_FILE.write_text(key, encoding="utf-8")

        self.assertTrue(lm.is_activated())
        self.assertEqual(lm.get_key(), key.replace("-", ""))


if __name__ == "__main__":
    unittest.main()
