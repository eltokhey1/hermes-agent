"""Behavioral verification of the Hermes Android APK static analyzer."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import warnings
import zipfile

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "optional-skills/security/android-apk-audit/scripts/apk_audit.py"
spec = importlib.util.spec_from_file_location("hermes_android_apk_audit", SCRIPT)
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


@pytest.fixture
def make_apk(tmp_path):
    def build(entries=None):
        target = tmp_path / "sample.apk"
        if entries is None:
            entries = {
                "AndroidManifest.xml": b'<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.example.app"><uses-permission android:name="android.permission.INTERNET"/></manifest>',
                "classes.dex": b"dex\n035\x00" + b"-" * 128,
                "lib/arm64-v8a/libdemo.so": b"\x7fELFsample",
            }
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in entries.items() if isinstance(entries, dict) else entries:
                z.writestr(name, data)
        return target
    return build


def test_authorization_fail_closed(make_apk):
    with pytest.raises(scan.AuditError, match="authorization_required"):
        scan.analyze_apk(make_apk())


def test_static_report_inventory_and_source_unchanged(make_apk):
    target = make_apk()
    original = target.read_bytes()
    report = scan.analyze_apk(target, authorized=True)
    assert report["status"] == "STATIC_CHECKPOINT"
    assert report["evidence"]["dex_files"] == ["classes.dex"]
    assert report["evidence"]["native_abis"] == ["arm64-v8a"]
    assert report["evidence"]["manifest"]["permissions"] == ["android.permission.INTERNET"]
    assert report["evidence"]["manifest"]["package"] == "org.example.app"
    assert target.read_bytes() == original
    assert sorted(p.name for p in target.parent.iterdir()) == ["sample.apk"]
    assert report["source"]["sha256"] == scan.hashlib.sha256(original).hexdigest()


def test_binary_manifest_unknown_not_fabricated(make_apk):
    path = make_apk({"AndroidManifest.xml": b"\x03\x00\x08\x00fake", "classes.dex": b"dex\n038\x00"})
    report = scan.analyze_apk(path, authorized=True)
    assert report["evidence"]["manifest"]["permissions"] is None
    assert report["evidence"]["manifest"]["format"] == "binary_axml"


@pytest.mark.parametrize("bad", ["../escape", "/abs/file", "C:/evil", "a/../b", "a\\..\\b", "x//b"])
def test_refuses_traversal_members(make_apk, bad):
    with pytest.raises(scan.AuditError, match="unsafe_zip_member_name"):
        scan.analyze_apk(make_apk({"AndroidManifest.xml": b"<manifest/>", bad: b"x"}), authorized=True)


def test_refuses_duplicate_members(tmp_path):
    path = tmp_path / "duplicate.apk"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("AndroidManifest.xml", b"<manifest/>")
            z.writestr("classes.dex", b"dex\n035\x00")
            z.writestr("classes.dex", b"dex\n038\x00")
    with pytest.raises(scan.AuditError, match="duplicate_zip_member"):
        scan.analyze_apk(path, authorized=True)


def test_refuses_high_compression_ratio(make_apk):
    path = make_apk({"AndroidManifest.xml": b"<manifest/>", "huge": b"A" * (2 * 1024 * 1024)})
    with pytest.raises(scan.AuditError, match="zip_compression_ratio_limit"):
        scan.analyze_apk(path, authorized=True)


def test_refuses_missing_manifest(make_apk):
    with pytest.raises(scan.AuditError, match="missing_android_manifest"):
        scan.analyze_apk(make_apk({"classes.dex": b"dex\n035\x00"}), authorized=True)


def test_refuses_nonzip_input(make_apk):
    path = make_apk()
    path.write_bytes(b"NOT AN APK")
    with pytest.raises(scan.AuditError, match="not_an_apk_zip"):
        scan.analyze_apk(path, authorized=True)


def test_cli_blocks_without_auth_and_refuses_overwrite(make_apk, tmp_path):
    path = make_apk()
    denied = subprocess.run([sys.executable, str(SCRIPT), "--apk", str(path)], capture_output=True, text=True)
    assert denied.returncode == 2
    assert json.loads(denied.stderr)["reason"] == "authorization_required"
    output = tmp_path / "report.json"
    first = subprocess.run([sys.executable, str(SCRIPT), "--apk", str(path), "--authorized", "--output", str(output)], capture_output=True, text=True)
    assert first.returncode == 0
    assert json.loads(output.read_text())["status"] == "STATIC_CHECKPOINT"
    original = output.read_bytes()
    again = subprocess.run([sys.executable, str(SCRIPT), "--apk", str(path), "--authorized", "--output", str(output)], capture_output=True, text=True)
    assert again.returncode == 2
    assert output.read_bytes() == original
