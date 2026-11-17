#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/fs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/wait.h>
#include <unistd.h>

static int commercial_bounded010(void (*worker)(void *), void *context, int milliseconds)
{
    (void)milliseconds;
    pid_t child = fork();
    assert(child >= 0);
    if (!child) { worker(context); _exit(0); }
    int state;
    assert(waitpid(child, &state, 0) == child && WIFEXITED(state));
    return WEXITSTATUS(state);
}

#include "oobe-data-snapshot-121.h"

int main(int argc, char **argv)
{
    assert(argc == 2 && chdir(argv[1]) == 0);
    int source = open("source", O_RDWR | O_CREAT | O_EXCL, 0600);
    int output = open("output", O_RDWR | O_CREAT | O_EXCL, 0600);
    const off_t size = 16 * 1024 * 1024;
    assert(source >= 0 && output >= 0 && ftruncate(source, size) == 0);
    const off_t positions[] = {0, 9 * 1024 * 1024 + 13, size - 4};
    for (unsigned i = 0; i < 3; ++i) assert(pwrite(source, "test", 4, positions[i]) == 4);
    assert(oobe_sparse_copy121(source, output, size) == 0);
    for (unsigned i = 0; i < 3; ++i) {
        char data[4];
        assert(pread(output, data, 4, positions[i]) == 4 && !memcmp(data, "test", 4));
    }
    unsigned char hole[4096] = {0}, check[4096];
    assert(pread(output, check, sizeof(check), 4 * 1024 * 1024) == sizeof(check));
    assert(!memcmp(check, hole, sizeof(check)));
    struct stat state;
    assert(fstat(output, &state) == 0 && state.st_size == size && state.st_blocks * 512 < size / 8);
    close(source); close(output);
    source = open("empty", O_RDWR | O_CREAT | O_EXCL, 0600);
    output = open("empty-copy", O_RDWR | O_CREAT | O_EXCL, 0600);
    assert(source >= 0 && output >= 0 && ftruncate(source, size) == 0);
    assert(oobe_sparse_copy121(source, output, size) == 0);
    assert(fstat(output, &state) == 0 && state.st_size == size && state.st_blocks == 0);
    assert(oobe_sparse_copy121(-1, output, size) == -1);
    close(source); close(output);
    /* Invalid descriptors must fail before mkdir or filesystem freeze. */
    oobe_snapshot121(-1);
    puts("SPARSE121_TESTS_PASS content holes tail empty invalid_descriptor");
    return 0;
}
