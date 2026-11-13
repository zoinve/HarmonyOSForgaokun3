#ifndef BAREMETAL_FREEDRENO_DMABUF_POLICY_001_H
#define BAREMETAL_FREEDRENO_DMABUF_POLICY_001_H
#include <limits.h>
#include <stdint.h>

/* This probe accepts only a small, single-plane, zero-offset linear RGBA BO. */
static int dmabuf_meta_ok(int fd, unsigned width, unsigned height,
                          unsigned planes, unsigned stride, unsigned offset,
                          uint64_t modifier)
{
    return fd >= 0 && width > 0 && width <= 4096 && height > 0 && height <= 4096
        && planes == 1 && stride >= width * 4 && stride <= INT_MAX
        && offset == 0 && modifier == 0;
}
#endif
