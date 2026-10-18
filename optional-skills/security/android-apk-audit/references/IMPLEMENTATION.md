# Hermes Android APK Audit — Design and rollout

## Provenance and scope

Independent scanner and optional Hermes skill inspired by the *workflow concepts*
in `newliver666/apk-reverse`, published under MIT. **No upstream code is copied
or vendored.** SourceForge mirror:
https://sourceforge.net/projects/apk-reverse.mirror/files/
Original project:
https://github.com/newliver666/apk-reverse

The upstream project is a guided Android reverse-engineering Agent Skill covering
DEX work, APK packaging, native diagnosis and runtime investigations. This new
Hermes P0 deliberately provides only a bounded **read-only** ZIP inventory.

## Integration shape

```text
Hermes CLI or gateway -> optional skill (G1 authorization)
                      -> Python 3.11+ stdlib script (G2)
                      -> bounded local APK ZIP reader (G3)
                      -> source SHA-256 baseline (G4)
                      -> JSON evidence report
```

No core-tool schema, persistent daemon, API token, network call, installation hook,
persistent process, or APK execution is added. Normal Hermes skill-discovery and
skill-install paths handle the optional skill. It is not loaded by default.

## CLI

```sh
python optional-skills/security/android-apk-audit/scripts/apk_audit.py \
  --apk sample-owned.apk --authorized --output report.json

python -m pytest -q tests/skills/test_android_apk_audit_skill.py
```

`--authorized` is an explicit declaration by the operator; the CLI itself
cannot independently verify legal ownership. No report file is overwritten.

After review and merge, a checkout with the optional skill available can use:
`hermes skills install official/security/android-apk-audit`. Begin a new Hermes
session after activation to preserve prompt cache integrity.

## Threat model / current protections

- Arbitrary APK inputs are untrusted; no extraction, subprocess, external upload,
  dynamic instrumentation, code execution, signing, or patching in P0.
- Reject traversal/absolute ZIP member paths, duplicate paths, symlink members,
  encrypted members, non-ZIP inputs, missing manifest, oversized archives, entry
  count/size/ratio violations.
- Limit text-manifest parse input; binary Android AXML remains unknown, not guessed.
- Hash the open APK and verify hash + file descriptor identity/size after analysis.
- Output file is optional, never overwritten; only a report is written.
- The scanner is a bounded static inventory, **not** a verdict of app safety,
  malware status, signature verification, installability, or runtime behavior.

Note: resource limits in P0 are *parser-level* bounds, **not** an operating
system sandbox. An untrusted APK should still be analyzed in a low-privilege,
offline disposable container or similarly isolated environment; CPU/memory
limits must be enforced by the host.

## Capability comparison

| Capability | Upstream apk-reverse | Hermes P0 |
| --- | --- | --- |
| Stepwise gate/evidence discipline | Yes | Yes, G1–G4 report |
| Static APK archive inventory | Yes | Yes |
| Source SHA-256 | Underlying tooling/evidence | Yes |
| AXML binary manifest parsing | Via external tools | Not implemented; UNKNOWN |
| DEX cross references, disassembly, decompilation | Guided optional tooling | Not implemented |
| Native/Flutter runtime diagnostics | Guided optional tooling | Not implemented |
| Repack, sign, patch | Guided optional tooling | Disabled |
| Rooted device / ADB / Frida | Guided optional tooling | Disabled |
| Output reproducibility and sandbox verification | Upstream evidence gates | Local synthetic tests; live E2E pending |

## Milestones and approval gates

P0 (this PR): optional skill, offline scanner, documented limits and behavior tests.
No production deployment or installation on the user's machine.

P1 (later, separate PR): add a read-only, pinned optional `aapt2` / `apkanalyzer`
adapter for binary AndroidManifest.xml; verify tool SHA-256, parse structured
output defensively, add real authorized sample fixture, and run a Docker
integration test with `--network none`, read-only input and resource limits.

P2 (later, separate PR): optional JADX/droidasc/DDC query adapters limited
to authorized local APKs; provenance, cost/time ceilings, and sampled
validation against independent tools. Native diagnostic capabilities require
separate sandbox, no secret environment, and manual approval.

P3 (not approved): any APK modification, re-signing, bypass of controls or
dynamic device operations. Require explicit scope, backup, differential tests,
and separate change approval before executing.

## Acceptance evidence

- 14 behavioral checks passed on synthetic APKs in an isolated artifact
  environment (the GitHub branch should still be tested by CI).
- No Windows machine run, real customer APK analysis or live Hermes
  installation has been performed.
- Merge and deployment require a reviewer + passing CI and isolated E2E.
