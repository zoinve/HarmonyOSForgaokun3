/* Diagnostic child only: record the original fault, then terminate as a failure. */
#define _GNU_SOURCE
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <ucontext.h>
#include <unistd.h>
#include <fcntl.h>
static void fault(int sig, siginfo_t *info, void *context)
{
    ucontext_t *uc = context;
    char text[1024];
    int n = snprintf(text, sizeof(text),
        "FRONTEND928_FAULT signal=%d code=%d address=%p pc=0x%lx lr=0x%lx sp=0x%lx x0=0x%lx x1=0x%lx\n",
        sig, info->si_code, info->si_addr, (unsigned long)uc->uc_mcontext.pc,
        (unsigned long)uc->uc_mcontext.regs[30], (unsigned long)uc->uc_mcontext.sp,
        (unsigned long)uc->uc_mcontext.regs[0], (unsigned long)uc->uc_mcontext.regs[1]);
    write(2, text, n);
    int fd = open("/proc/self/maps", O_RDONLY);
    if (fd >= 0) {
        while ((n = read(fd, text, sizeof(text))) > 0) write(2, text, n);
        close(fd);
    }
    _exit(128 + sig);
}
__attribute__((constructor)) static void install(void)
{
    struct sigaction action = {0};
    action.sa_sigaction = fault;
    action.sa_flags = SA_SIGINFO;
    sigemptyset(&action.sa_mask);
    sigaction(SIGBUS, &action, NULL);
    sigaction(SIGSEGV, &action, NULL);
    write(2, "FRONTEND928_DIAGNOSTIC_READY\n", 29);
}
