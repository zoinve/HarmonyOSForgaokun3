/* Observe an original executable's real exec transition; do not manufacture native tokens. */
static void samgr_exec_026(void)
{
    require(!mount(NULL, "/sdk-system", NULL, MS_REMOUNT | MS_RDONLY | MS_NODEV | MS_NOSUID, "noload"),
            "enable original executable on still-read-only SDK filesystem");
    struct statvfs flags;
    require(!statvfs("/sdk-system", &flags) && (flags.f_flag & ST_RDONLY) && !(flags.f_flag & ST_NOEXEC),
            "read-only executable filesystem flags");
    int error_pipe[2];
    require(!pipe2(error_pipe, O_CLOEXEC | O_NONBLOCK), "bounded exec-result pipe");
    pid_t child = fork();
    require(child >= 0, "fork original samgr executable");
    if (!child) {
        close(error_pipe[0]);
        int error = 0;
        int attr = open("/proc/self/attr/exec", O_WRONLY | O_CLOEXEC);
        const char context[] = "u:r:samgr:s0";
        gid_t groups[] = {5555, 1000, 3009, 1065};
        if (attr < 0 || write(attr, context, sizeof(context)-1) != sizeof(context)-1) error = errno;
        if (attr >= 0) close(attr);
        if (!error && (setgroups(4, groups) || setgid(5555) || setuid(5555))) error = errno;
        if (!error) execl("/system/bin/samgr", "/system/bin/samgr", (char *)NULL);
        if (!error) error = errno;
        (void)write(error_pipe[1], &error, sizeof(error));
        _exit(202);
    }
    close(error_pipe[1]);
    int observed = 0, exited = 0, status = 0, exec_error = 0, exec_pipe_closed = 0;
    char path[128], value[8192];
    for (unsigned i = 0; i < 2000; ++i) {
        snprintf(path, sizeof(path), "/proc/%ld/attr/current", (long)child);
        if (text(path, value, sizeof(value)) > 0 && !strncmp(value, "u:r:samgr:s0", 12)) {
            snprintf(path, sizeof(path), "/proc/%ld/status", (long)child);
            if (text(path, value, sizeof(value)) > 0) {
                char *uids = strstr(value, "Uid:");
                char *gids = strstr(value, "Gid:");
                unsigned ur, ue, us, uf, gr, ge, gs, gf;
                if (uids && gids && sscanf(uids, "Uid: %u %u %u %u", &ur, &ue, &us, &uf) == 4 &&
                    sscanf(gids, "Gid: %u %u %u %u", &gr, &ge, &gs, &gf) == 4 &&
                    ur == 5555 && ue == 5555 && us == 5555 && uf == 5555 &&
                    gr == 5555 && ge == 5555 && gs == 5555 && gf == 5555) observed = 1;
            }
        }
        ssize_t n = read(error_pipe[0], &exec_error, sizeof(exec_error));
        if (n == 0) exec_pipe_closed = 1;
        if (n == sizeof(exec_error)) break;
        pid_t result = waitpid(child, &status, WNOHANG);
        require(result >= 0, "observe original samgr lifecycle");
        if (result == child) { exited = 1; break; }
        struct timespec interval = {0, 1000000};
        nanosleep(&interval, NULL);
    }
    close(error_pipe[0]);
    if (!exited) {
        require(!kill(child, SIGTERM) || errno == ESRCH, "bounded stop of guest-only samgr probe");
        for (unsigned i = 0; i < 100; ++i) {
            pid_t result = waitpid(child, &status, WNOHANG);
            require(result >= 0, "reap stopped original samgr");
            if (result == child) { exited = 1; break; }
            struct timespec interval = {0, 1000000};
            nanosleep(&interval, NULL);
        }
        if (!exited) {
            require(!kill(child, SIGKILL) || errno == ESRCH, "bounded fallback guest-only stop");
            require(waitpid(child, &status, 0) == child, "reap guest-only samgr fallback");
        }
    }
    dprintf(1, "SELINUX026_EXEC_RESULT domain_uid_gid_observed=%d exec_pipe_closed=%d exec_errno=%d child_status=%d services_ready=0\n",
            observed, exec_pipe_closed, exec_error, status);
    require(!exec_error && exec_pipe_closed && observed, "original samgr actual exec domain and unprivileged credentials");
    dprintf(1, "SELINUX026_EXEC_PASS original_binary=1 actual_samgr_domain=1 uid=5555 gid=5555 "
               "tokens_not_fabricated=1 policy_unchanged=1 services_ready=0 desktop_not_tested=1\n");
}
