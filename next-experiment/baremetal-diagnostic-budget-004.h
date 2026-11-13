/* Admission control only: synchronous kernel I/O may still exceed any budget. */
#ifndef BAREMETAL_DIAGNOSTIC_BUDGET_004_H
#define BAREMETAL_DIAGNOSTIC_BUDGET_004_H
#include <math.h>

static inline int diag_budget_allow(double start, double now, unsigned total,
                                    unsigned reserve, unsigned requested)
{
    if (!isfinite(start) || !isfinite(now) || start < 0 || now < start ||
        !requested || reserve >= total || requested > total - reserve) return 0;
    return now - start <= (double)(total - reserve - requested);
}
#endif
