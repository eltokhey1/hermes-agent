# Hermes Windows P0 read-only inventory (v2) — owner handoff

This is an **inventory**, NOT a readiness/acceptance certificate. It is intentionally safe to run before P0 backup and restore because it does not change the machine and does not run third-party executables. It probes only a localhost TCP port; a listener is not identity verification.

In a **local Windows PowerShell session**, inspect the `.ps1` file and run it by its full trusted path or by copying the source into the shell. Example for a user-chosen folder:

```powershell
& 'C:\YOUR_FOLDER\Hermes_Windows_ReadOnly_Preflight_v2.ps1'
```

Expected output: one JSON object, with no secrets, filenames, absolute paths, hostname, or account IDs. The user's local agent installation and model names are not exported. You may paste this JSON into ChatGPT after checking it yourself.

- `tools_found`: only command presence; not a tested integration.
- `profile_markers`: only marker existence; backups are not tested or verified.
- `local_loopback.port_11434_listening`: connection to local TCP port; is not evidence Ollama owns the port.
- `acceptance`: `NOT_TESTED` for all consequential P0/P1 gates until independently executed on the actual owner machine.
- `production_ready`: **always false**, even if all indicators are true.

## The actual host acceptance sequence (separate, not automatically performed)

1. Confirm actual Hermes home/profile (including custom `HERMES_HOME`) privately and inventory the installation. Do not paste the path, local `.env`, credentials or `state.db` into public GitHub.
2. Create a protected copy using a trusted local method; verify files/permissions; **restore into a separate temporary isolated destination** and run a functional read-only recovery check, never over the live installation.
3. Demonstrate ACL write denial and secret isolation using the actual intended process identity. Test failure/timeout/corruption/ESTOP behavior (fail closed).
4. Run real Hermes P1 recovery & acceptance suites with fake data and an independent protected ledger anchor. Do not retry uncertain external effects.
5. After P0/P1 evidence, inventory Ollama models, Kilo and OpenCode in the local sandbox, and run one bounded code-edit + test + verifier workflow in Shadow mode. No auto paid fallback.
6. Only after these steps can a **separately authenticated human** review enabling external effects. No production deployment, paid API calls, sending or main merge is authorized by this inventory.

All current output is safe diagnostics, and absence of any gate evidence means **UNKNOWN/NO-GO** rather than PASS. Do not count GitHub-hosted Windows runner success as evidence about the owner's Windows machine.
