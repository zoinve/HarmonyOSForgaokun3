"""Generate a fresh 004 candidate; do not modify any prior source or archive."""
from pathlib import Path
import hashlib


def build_source(parent):
    assert hashlib.sha256(parent.encode()).hexdigest() == '369e23d03a25345ce9388a7c3e13641566c6ac80daad2c28909207223c3056fa'
    header = (Path(__file__).resolve().parent / 'baremetal-diagnostic-budget-004.h').read_text()
    changes = {
        '#include <unistd.h>': '#include <unistd.h>\n#include <time.h>\n' + header,
        'static unsigned snapshot_id;': '''static unsigned snapshot_id;
static double budget_start = -1;

static int budget_ready(unsigned requested)
{
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now)) return 0;
    return diag_budget_allow(budget_start, now.tv_sec + now.tv_nsec / 1e9,
                             180, 30, requested);
}''',
        '    dprintf(1, "PHASE_BEGIN %s\\n", name);': '''    if (!budget_ready(timeout)) {
        dprintf(1, "BUDGET_REFUSED phase=%s\\n", name);
        return 124;
    }
    dprintf(1, "PHASE_BEGIN %s\\n", name);''',
        '    int status = diag_run(argv, timeout);': '''    /* A log flush can consume time: recheck before actually spawning. */
    if (!budget_ready(timeout)) {
        dprintf(1, "BUDGET_REFUSED phase=%s after_snapshot=1\\n", name);
        return 124;
    }
    int status = diag_run(argv, timeout);''',
        '    int fd = open("/run/blkid-export",': '''    if (!budget_ready(3)) return -1;
    int fd = open("/run/blkid-export",''',
        '    if (mount("/dev/nvme0n1p4",': '''    /* Admission only, not a bound on synchronous mount or subsequent I/O. */
    if (!budget_ready(15)) return -1;
    if (mount("/dev/nvme0n1p4",''',
        '    dprintf(1, "NATIVE_DIAGNOSTIC_BEGIN': '''    struct timespec begin;
    if (clock_gettime(CLOCK_MONOTONIC, &begin)) hold();
    budget_start = begin.tv_sec + begin.tv_nsec / 1e9;
    dprintf(1, "NATIVE_DIAGNOSTIC_BEGIN''',
    }
    for old, new in changes.items():
        assert parent.count(old) == 1, old
        parent = parent.replace(old, new)
    return parent
