import tempfile
import unittest
from pathlib import Path

from fitness_manager.crypto import decrypt_file, encrypt_file


class CryptoTests(unittest.TestCase):
    def test_authenticated_encryption_roundtrip_and_tamper_detection(self):
        try:
            import cryptography  # noqa: F401
        except ImportError:
            self.skipTest("optional cryptography dependency is not installed")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.sqlite"
            encrypted = root / "source.sqlite.enc"
            restored = root / "restored.sqlite"
            source.write_bytes(b"synthetic sqlite backup bytes")
            encrypt_file(source, encrypted, "test-passphrase-not-for-production")
            decrypt_file(encrypted, restored, "test-passphrase-not-for-production")
            self.assertEqual(source.read_bytes(), restored.read_bytes())
            tampered = bytearray(encrypted.read_bytes())
            tampered[-1] ^= 1
            encrypted.write_bytes(tampered)
            with self.assertRaises(Exception):
                decrypt_file(encrypted, restored, "test-passphrase-not-for-production")


if __name__ == "__main__":
    unittest.main()
