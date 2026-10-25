"""Allowlisted worker exit diagnostics; never record worker output or secrets."""

def classify_worker_exit(returncode):
    """Return a stable, non-sensitive label for a subprocess return code."""
    if not isinstance(returncode, int) or isinstance(returncode, bool):
        raise TypeError("returncode must be int")
    if returncode == 0:
        return "WORKER_OK"
    if returncode < 0:
        return "WORKER_SIGNAL"
    if returncode > 255:
        return "WORKER_EXIT_OUT_OF_RANGE"
    return f"WORKER_EXIT_{returncode}"
