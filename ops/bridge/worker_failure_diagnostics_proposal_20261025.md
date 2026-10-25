# Hermes Bridge worker failure diagnostics — sandbox-only proposal

Status: PLANNED / NOT INSTALLED. Production remains HOLD.

## Verified gap
The pinned supervisor's `run_once` captures worker stdout/stderr, but returns only `WORKER_EXIT_NONZERO` for a nonzero exit code. The last observed worker failures are intermittent; GitHub API connectivity succeeds independently. The root cause is unknown.

## Minimal patch for a future, separately versioned supervisor
Keep the worker pinned and unchanged. Never write raw stdout, stderr, environment, tokens, inbox payloads, or document contents to disk. Replace the generic failure return in `run_once` with a coarse reason category based only on the exit code:

```python
    if result.returncode != 0:
        return result.returncode, f"WORKER_EXIT_{result.returncode}"
```

This improves exit-code observability but **does not** reveal the root cause. Do not infer GitHub/network/auth failure from the exit code alone. To diagnose those, a future worker version must emit *explicit allowlisted error codes* at known exception boundaries; never classify from raw stderr text.

## Required gates
1. Keep existing running supervisor and its pinned SHA256 unchanged.
2. Add tests for exit 0 with valid final line, nonzero exit, timeout, OSError, unexpected stderr, malformed final line, and secret-bearing stderr never persisted.
3. Test one-instance lock and 5-consecutive-failure STOPPED behavior.
4. Independently review new supervisor hash and update deployment pin only after tests.
5. No auto-replacement, Windows service changes, merge, or production activation.

Evidence: previous scans 18–20 PASS; later intermittent `WORKER_EXIT_NONZERO`; GitHub API check exit 0; root cause UNKNOWN.
