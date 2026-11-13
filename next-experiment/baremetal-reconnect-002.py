"""Immediate, bounded SSH observation; never issue a reboot or infer diagnostic success."""
import time
import uuid


def wait_for_return(before_boot_id, probe, timeout=600, interval=1):
    assert timeout > 0 and interval > 0
    uuid.UUID(before_boot_id)
    start = time.monotonic()
    attempts = []
    while time.monotonic() - start < timeout:
        elapsed = time.monotonic() - start
        state = probe()
        valid = False
        if isinstance(state, dict):
            try:
                identity = str(uuid.UUID(state.get('boot_id', '')))
                valid = (identity != before_boot_id and bool(state.get('kernel'))
                         and isinstance(state.get('cmdline'), str)
                         and 'harmony.diag=1' not in state['cmdline'].split())
            except (ValueError, TypeError, AttributeError):
                pass
        attempts.append(dict(started_seconds=elapsed, state=state, new_boot_observed=valid))
        if valid:
            return dict(returned=state, attempts=attempts, timed_out=False)
        remaining = timeout - (time.monotonic() - start)
        if remaining > 0:
            time.sleep(min(interval, remaining))
    return dict(returned=None, attempts=attempts, timed_out=True)
