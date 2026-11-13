#ifndef BAREMETAL_RENDER_NODE_POLICY_001_H
#define BAREMETAL_RENDER_NODE_POLICY_001_H
#include <sys/stat.h>
#include <sys/sysmacros.h>
static int native_render_identity001(const struct stat *state)
{
    return state && S_ISCHR(state->st_mode) &&
        major(state->st_rdev) == 226 && minor(state->st_rdev) == 128;
}
#endif
