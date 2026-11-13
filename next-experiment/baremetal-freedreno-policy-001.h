#ifndef BAREMETAL_FREEDRENO_POLICY_001_H
#define BAREMETAL_FREEDRENO_POLICY_001_H
#include <string.h>

static int freedreno_renderer_ok(const char *renderer)
{
    return renderer && !strcmp(renderer, "FD690");
}

static int freedreno_pixels_ok(const unsigned char *center, const unsigned char *corner)
{
    return center[0] > 240 && center[1] < 16 && center[2] < 16 && center[3] > 240 &&
           corner[0] < 16 && corner[1] < 16 && corner[2] > 240 && corner[3] > 240;
}
#endif
