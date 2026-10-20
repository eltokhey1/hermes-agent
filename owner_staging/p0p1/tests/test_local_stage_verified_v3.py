"""Synthetic filesystem regression tests for the pinned-bytes V3 ZIP staging fix."""
from __future__ import annotations
import io
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import local_stage_verified_v3 as v3


class VerifiedBytesStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _zip(self, path: Path, members: dict[str, str]) -> Path:
        with zipfile.ZipFile(path, 'w') as archive:
            for name, value in members.items():
                archive.writestr(name, value)
        return path

    def _stage(self, path: Path, target_name: str = 'stage'):
        return v3.stage_archive(path, v3.hash_file(path), self.root / target_name)

    def test_success_preserves_original_and_writes_nonacceptance_receipt(self):
        source = self._zip(self.root / 'safe.zip', {'dir/a.txt': 'good'})
        before = source.read_bytes()
        receipt = self._stage(source)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual((self.root / 'stage/dir/a.txt').read_text(), 'good')
        self.assertEqual(receipt['gate'], 'NO-GO')
        self.assertIn('"host_verified": false', (self.root / 'stage/STAGING_RECEIPT.json').read_text())

    def test_swapping_zip_at_decompression_does_not_replace_pinned_content(self):
        safe = self._zip(self.root / 'safe.zip', {'safe.txt': 'SAFE'})
        attacker = self._zip(self.root / 'swap.zip', {'swapped.txt': 'ATTACKER'})
        expected = v3.hash_file(safe)
        real_open = zipfile.ZipFile
        swapped = []

        def swap_at_open(archive, *args, **kwargs):
            if isinstance(archive, io.BytesIO):
                shutil.copyfile(attacker, safe)
                swapped.append(True)
            return real_open(archive, *args, **kwargs)

        with patch.object(v3.zipfile, 'ZipFile', side_effect=swap_at_open):
            v3.stage_archive(safe, expected, self.root / 'stage')
        self.assertTrue(swapped)
        self.assertEqual((self.root / 'stage/safe.txt').read_text(), 'SAFE')
        self.assertFalse((self.root / 'stage/swapped.txt').exists())
        self.assertNotEqual(v3.hash_file(safe), expected)

    def test_hash_and_unzip_do_not_reopen_original_archive(self):
        source = self._zip(self.root / 'safe.zip', {'safe.txt': 'ok'})
        original_hash = v3.hash_file
        def ensure_source_not_reopened(path):
            self.assertNotEqual(Path(path), source, 'source archive rehashed after pinning')
            return original_hash(path)
        with patch.object(v3, 'hash_file', side_effect=ensure_source_not_reopened):
            v3.stage_archive(source, __import__('hashlib').sha256(source.read_bytes()).hexdigest(), self.root / 'stage')
        self.assertTrue((self.root / 'stage/safe.txt').exists())

    def test_hash_mismatch_is_fail_closed_without_artifacts(self):
        source = self._zip(self.root / 'safe.zip', {'file': 'ok'})
        with self.assertRaises(ValueError):
            v3.stage_archive(source, '0' * 64, self.root / 'stage')
        self.assertFalse((self.root / 'stage').exists())

    def test_bounded_compressed_archive_rejected(self):
        source = self._zip(self.root / 'safe.zip', {'file': 'ok'})
        with patch.object(v3, 'MAX_ZIP_BYTES', 5):
            with self.assertRaises(ValueError):
                self._stage(source)
        self.assertFalse((self.root / 'stage').exists())

    def test_rejects_nonarchive_bytes(self):
        source = self.root / 'safe.zip'
        source.write_bytes(b'not an archive')
        with self.assertRaises(zipfile.BadZipFile):
            self._stage(source)
        self.assertFalse((self.root / 'stage').exists())

    def test_rejects_windows_case_collision(self):
        source = self._zip(self.root / 'safe.zip', {'A.txt': 'a', 'a.txt': 'b'})
        with self.assertRaises(ValueError):
            self._stage(source)

    def test_rejects_windows_device_name(self):
        source = self._zip(self.root / 'safe.zip', {'CON.txt': 'danger'})
        with self.assertRaises(ValueError):
            self._stage(source)

    def test_rejects_absolute_path_and_traversal(self):
        for name in ('/outside.txt', '../outside.txt'):
            with self.subTest(name=name):
                source = self._zip(self.root / 'safe.zip', {name: 'danger'})
                with self.assertRaises(ValueError):
                    self._stage(source)
                self.assertFalse((self.root / 'stage').exists())

    def test_existing_stage_is_never_overwritten(self):
        source = self._zip(self.root / 'safe.zip', {'file': 'ok'})
        target = self.root / 'stage'
        target.mkdir()
        (target / 'keep').write_text('keep')
        with self.assertRaises(FileExistsError):
            self._stage(source)
        self.assertEqual((target / 'keep').read_text(), 'keep')

    def test_reject_symlink_source(self):
        source = self._zip(self.root / 'safe.zip', {'file': 'ok'})
        symlink = self.root / 'source-link.zip'
        try:
            symlink.symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unsupported')
        with self.assertRaises(ValueError):
            self._stage(symlink)

    def test_reject_symlink_destination_ancestor(self):
        source = self._zip(self.root / 'safe.zip', {'file': 'ok'})
        real = self.root / 'real'
        real.mkdir()
        alias = self.root / 'alias'
        try:
            alias.symlink_to(real, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unsupported')
        with self.assertRaises(ValueError):
            v3.stage_archive(source, v3.hash_file(source), alias / 'stage')

    def test_rejects_corrupt_stored_payload(self):
        source = self._zip(self.root / 'safe.zip', {'file': 'ok'})
        data = source.read_bytes().replace(b'ok', b'xx', 1)
        source.write_bytes(data)
        with self.assertRaises((zipfile.BadZipFile, ValueError)):
            self._stage(source)
        self.assertFalse((self.root / 'stage').exists())


if __name__ == '__main__':
    unittest.main()
