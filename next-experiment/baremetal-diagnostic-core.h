#ifndef BAREMETAL_DIAGNOSTIC_CORE_H
#define BAREMETAL_DIAGNOSTIC_CORE_H
int diag_gate(int pid, const char *release, const char *cmdline);
int diag_identity(const char *exported);
int diag_new_run(int parent, const char *name);
int diag_run(char *const argv[], unsigned seconds);
#endif
