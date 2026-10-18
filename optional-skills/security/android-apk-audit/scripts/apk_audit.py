#!/usr/bin/env python3
"""Bounded, read-only Android APK inventory for an authorized local file.

No subprocesses, APK execution, extraction, decompilation, patching or network I/O.
Compatible with Python 3.11+. No third-party dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import xml.etree.ElementTree as ET
import zipfile

SCHEMA_VERSION = "1.0"
MAX_APK_BYTES = 250 * 1024 * 1024
MAX_ENTRIES = 8_000
MAX_TOTAL_UNCOMPRESSED = 768 * 1024 * 1024
MAX_MEMBER_UNCOMPRESSED = 128 * 1024 * 1024
MAX_RATIO = 250
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
DRIVE_RE = re.compile(r"^[a-zA-Z]:")


class AuditError(ValueError):
    """A security gate or APK-format invariant failed."""


def _sha256(handle) -> str:
    handle.seek(0)
    h = hashlib.sha256()
    while True:
        data = handle.read(1024 * 1024)
        if not data:
            break
        h.update(data)
    return h.hexdigest()


def _safe_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    parts = normalized.split("/")
    return bool(name) and not normalized.startswith("/") and not DRIVE_RE.match(normalized) \
        and all(part not in ("", ".", "..") for part in (parts[:-1] if normalized.endswith("/") else parts)) \
        and "\x00" not in name and all(ord(c) >= 32 for c in name)


def _validate_entries(entries: list[zipfile.ZipInfo]) -> None:
    if not entries or len(entries) > MAX_ENTRIES:
        raise AuditError("zip_entry_limit")
    total = 0
    seen = set()
    for item in entries:
        if not _safe_member(item.filename):
            raise AuditError("unsafe_zip_member_name")
        ident = item.filename.replace("\\", "/").casefold()
        if ident in seen:
            raise AuditError("duplicate_zip_member")
        seen.add(ident)
        if item.flag_bits & 1:
            raise AuditError("encrypted_zip_member")
        mode = (item.external_attr >> 16) & 0xFFFF
        if stat.S_IFMT(mode) == stat.S_IFLNK:
            raise AuditError("symlink_zip_member")
        if item.file_size > MAX_MEMBER_UNCOMPRESSED:
            raise AuditError("oversized_zip_member")
        total += item.file_size
        if total > MAX_TOTAL_UNCOMPRESSED:
            raise AuditError("zip_uncompressed_limit")
        if item.file_size > 1024 * 1024 and item.file_size / max(1, item.compress_size) > MAX_RATIO:
            raise AuditError("zip_compression_ratio_limit")


def _manifest_info(archive: zipfile.ZipFile, item: zipfile.ZipInfo) -> dict:
    if item.file_size > MAX_MANIFEST_BYTES:
        raise AuditError("manifest_size_limit")
    with archive.open(item) as fp:
        raw = fp.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) != item.file_size:
        raise AuditError("truncated_manifest")
    if raw[:4] == b"\x03\x00\x08\x00":
        return {"format": "binary_axml", "permissions": None, "package": None,
                "note": "Permissions and exported components NOT decoded; use approved aapt2 tooling separately."}
    # Android binary AXML is not parsed here. Reject entity expansion even for
    # the synthetic text-manifest path before touching an XML parser.
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise AuditError("manifest_dtd_or_entity_forbidden")
    try:
        tree = ET.fromstring(raw)
    except ET.ParseError:
        return {"format": "unrecognized", "permissions": None, "package": None,
                "note": "Manifest unreadable; cannot infer permissions."}
    if tree.tag != "manifest":
        return {"format": "unrecognized", "permissions": None, "package": None,
                "note": "Root element is not manifest."}
    permissions = sorted({p.get(ANDROID_NS + "name") for p in tree.findall("uses-permission")
                          if p.get(ANDROID_NS + "name")})
    return {"format": "text_xml", "permissions": permissions,
            "package": tree.get("package"), "note": "Text manifest only; runtime permissions not verified."}


def analyze_apk(apk_path: str | Path, *, authorized: bool = False) -> dict:
    """Return an evidence-bounded JSON-compatible report. Raise AuditError on unsafe input.

    'authorized=True' must follow an explicit user/owner authorization check in
    the calling program. Merely possessing an APK file is not authorization.
    """
    if not authorized:
        raise AuditError("authorization_required")
    path = Path(apk_path)
    if path.suffix.lower() != ".apk" or path.is_symlink() or not path.is_file():
        raise AuditError("local_regular_apk_required")
    try:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            if not 0 < before.st_size <= MAX_APK_BYTES:
                raise AuditError("apk_size_limit")
            magic = handle.read(4)
            if magic != b"PK\x03\x04":
                raise AuditError("not_an_apk_zip")
            source_sha256 = _sha256(handle)
            try:
                with zipfile.ZipFile(handle, mode="r") as archive:
                    entries = archive.infolist()
                    _validate_entries(entries)
                    files = {info.filename: info for info in entries if not info.is_dir()}
                    if "AndroidManifest.xml" not in files:
                        raise AuditError("missing_android_manifest")
                    manifest = _manifest_info(archive, files["AndroidManifest.xml"])
                    dex = sorted(p for p in files if re.fullmatch(r"classes(?:\d+)?\.dex", p))
                    native = sorted(p for p in files if p.startswith("lib/") and p.endswith(".so"))
                    abis = sorted({p.split("/")[1] for p in native if len(p.split("/")) >= 3})
                    signatures = sorted(p for p in files if re.fullmatch(r"META-INF/[^/]+\.(?:RSA|DSA|EC|SF)", p, flags=re.I))
                    invalid_dex = []
                    for name in dex:
                        with archive.open(files[name]) as fp:
                            hdr = fp.read(8)
                        if not (len(hdr) == 8 and hdr.startswith(b"dex\n") and hdr[4:7].isdigit() and hdr[-1:] == b"\x00"):
                            invalid_dex.append(name)
                    evidence = {
                        "zip_entries": len(entries),
                        "dex_files": dex,
                        "invalid_dex_headers": invalid_dex,
                        "native_abis": abis,
                        "native_library_count": len(native),
                        "resource_table_present": "resources.arsc" in files,
                        "v1_signature_metadata_files": signatures,
                        "manifest": manifest,
                    }
            except (zipfile.BadZipFile, RuntimeError, EOFError, OSError, ValueError) as exc:
                if isinstance(exc, AuditError):
                    raise
                raise AuditError("invalid_or_corrupt_apk_zip") from exc
            if _sha256(handle) != source_sha256:
                raise AuditError("apk_mutated_during_read")
            after = os.fstat(handle.fileno())
            if (before.st_dev, before.st_ino, before.st_size) != (after.st_dev, after.st_ino, after.st_size):
                raise AuditError("apk_mutated_during_read")
    except OSError as exc:
        raise AuditError("apk_read_error") from exc

    warnings = ["Static ZIP inventory only: this does not establish app safety, behavior, or installability.",
                "APK signature validity (including v2/v3/v4) and installed-device behavior are NOT checked."]
    if manifest["format"] != "text_xml":
        warnings.append("Binary/unrecognized manifest: package name, permission list and exported components unknown.")
    if invalid_dex:
        warnings.append("At least one DEX header was not recognized; decompilation was not attempted.")
    if not dex:
        warnings.append("No top-level classes*.dex found; this may be a resource-only or split APK.")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "STATIC_CHECKPOINT",
        "mode": "read_only_no_execution_no_network",
        "source": {"filename": path.name, "sha256": source_sha256, "size_bytes": before.st_size},
        "gates": {
            "G1_scope": "PASS: explicit authorization asserted; local APK selected; deliverable is static report",
            "G2_environment": "PASS: stdlib-only inspection; no external tool invoked",
            "G3_target": "PASS: APK ZIP inventory and manifest member identified",
            "G4_baseline": "PASS: input hash stable; no patch/build performed (not applicable in read-only mode)",
        },
        "evidence": evidence,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only, bounded audit of authorized Android APK files")
    parser.add_argument("--apk", required=True, help="Path to a local .apk")
    parser.add_argument("--authorized", action="store_true", help="Affirm ownership or written permission")
    parser.add_argument("--output", help="Write JSON report to this local path (otherwise stdout)")
    args = parser.parse_args(argv)
    try:
        result = analyze_apk(args.apk, authorized=args.authorized)
    except AuditError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}), file=sys.stderr)
        return 2
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        if output.exists():
            print(json.dumps({"status": "BLOCKED", "reason": "output_exists_no_overwrite"}), file=sys.stderr)
            return 2
        try:
            with output.open("x", encoding="utf-8") as fp:
                fp.write(payload)
        except OSError:
            print(json.dumps({"status": "BLOCKED", "reason": "report_write_error"}), file=sys.stderr)
            return 2
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
