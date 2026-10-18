---
name: android-apk-audit
description: "Inspect authorized Android APKs without running code."
version: 0.1.0
author: Mohamed Eltokhey, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
category: security
triggers:
  - "analyze my Android APK"
  - "audit an Android APK"
  - "inspect app manifest and DEX inventory"
toolsets:
  - terminal
  - file
metadata:
  hermes:
    tags: [Android, APK, Security, Static-Analysis]
    category: security
    related_skills: []
---

# Android APK Audit Skill

Inventory an APK using the bounded Python stdlib scanner bundled with this skill.
This is **not** a decompiler, exploit tool, APK repacker, or proof that an app is safe.
It adapts the four-gate, evidence-first workflow of `newliver666/apk-reverse`
without copying its implementation or invoking third-party executables.

## When to Use

Use when the user owns an Android app or is explicitly authorized to inspect an APK.
Use `read_file` for generated local JSON, and `terminal` to run the scanner.
Do not use for iOS IPA files or claim runtime observations from a static inventory.

## Prerequisites

- Confirm ownership or written authorization for the specific APK before analysis.
- A local `.apk` file and Python 3.11+.
- Resolve this skill's installed folder (`SKILL_DIR`) from the skill path shown by Hermes.
- No Java, JADX, Apktool, emulator, credentials, network, or extra packages are required.

## How to Run

Invoke using `terminal` only after the authorization gate is satisfied:

```powershell
python "SKILL_DIR/scripts/apk_audit.py" --apk "PATH_TO_AUTHORIZED.apk" --authorized
```

To explicitly save a report, append `--output "report.json"`; output files
are never overwritten. A missing `--authorized` fails closed.

## Quick Reference

| Gate | Required evidence | Action on failure |
| --- | --- | --- |
| G1 scope | authorization, exact local APK, static deliverable | Stop |
| G2 environment | Python stdlib scanner available | Stop |
| G3 target | bounded ZIP inventory and AndroidManifest.xml | Stop |
| G4 baseline | SHA-256 stable before and after, no changes | Stop |

Scanner failure is JSON on stderr and exit code 2; success outputs JSON on stdout.
The result status is deliberately `STATIC_CHECKPOINT`, not `VERIFIED_APP`.

## Procedure

1. **Classify** the deliverable. This skill supports only a read-only evidence
   report. Repacking, hooking, bypassing controls, and runtime testing require
   separate approval and an isolated environment.
2. **Authorize** scope (G1). A downloaded APK is not proof of permission.
3. **Check the environment** (G2) via `terminal` and the Python interpreter;
   do not auto-install packages or modify PATH.
4. **Collect inventory** (G3) with the bundled scanner once. It bounds ZIP
   entries, APK size, member sizes and ratios, and refuses traversal paths,
   duplicates, symlinks, and encrypted members.
5. **Record baseline** (G4). SHA-256 and inventory only; never extract,
   execute, patch, sign, or send the APK to any external service.
6. **Summarize** evidenced facts, partial observations, and unknowns.
   If AndroidManifest.xml is binary AXML, its permissions and package
   identity remain unknown in this P0.

## Pitfalls

- `META-INF/*.RSA` is signature *metadata*, not validation of signatures.
- Binary AXML is not text XML; never invent declared permissions or exports.
- DEX header bytes do not establish source code semantics or app safety.
- Never upload a customer's APK to SaaS services without separate approval.
- After two failures of the same type, stop and revise the hypothesis.
- Do not call the artifact installable or safe without independent proof.

## Verification

Use `terminal` to run
`python -m pytest -q tests/skills/test_android_apk_audit_skill.py` from this repo.
Only synthetic, authorized APKs belong in version-controlled test fixtures.
Run end-to-end smoke tests in a separately approved sandbox before production.

To install after review and merge:
`hermes skills install official/security/android-apk-audit`.
This capability remains optional and inactive until installed in a Hermes environment.
