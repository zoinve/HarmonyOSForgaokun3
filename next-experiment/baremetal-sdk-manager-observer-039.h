/* A bounded genuine handle-0 query. Never register a manager or alter SDK tokens. */
static void observer_require_039(int ok, const char *message)
{
    if (!ok) {
        dprintf(2, "ORIGINAL_INIT039_OBSERVER_FAIL %s errno=%d\n", message, errno);
        _exit(1);
    }
}

static void manager_observer_039(void)
{
    char context[512], enforcing[32];
    int loaded = 0;
    for (unsigned i = 0; i < 200; ++i) {
        if (read_path("/proc/self/attr/current", context, sizeof(context)) > 0 &&
            strstr(context, "u:r:kernel:s0")) { loaded = 1; break; }
        struct timespec interval = {0, 100000000}; nanosleep(&interval, NULL);
    }
    observer_require_039(loaded, "original init must load a policy before observer transition");
    int attr = open("/proc/self/attr/current", O_WRONLY | O_CLOEXEC);
    const char init_context[] = "u:r:init:s0";
    observer_require_039(attr >= 0 && write(attr, init_context, sizeof(init_context)-1) == sizeof(init_context)-1,
                         "policy-authorized kernel to init observer transition");
    close(attr);
    observer_require_039(read_path("/proc/self/attr/current", context, sizeof(context)) > 0 &&
                         strstr(context, "u:r:init:s0") != NULL, "actual observer init domain");
    int console = open("/dev/console", O_RDWR | O_CLOEXEC);
    observer_require_039(console >= 0, "observer opens original console under policy");
    for (int i = 0; i < 3; ++i) observer_require_039(dup2(console, i) >= 0, "observer console descriptors");
    close(console);
    observer_require_039(read_path("/sys/fs/selinux/enforce", enforcing, sizeof(enforcing)) > 0 &&
                         enforcing[0] == '1', "enforcement before manager query");
    dprintf(1, "ORIGINAL_INIT039_OBSERVER domain=u:r:init:s0 enforcing=1 replacement_manager=0 tokens_modified=0\n");
    struct timespec start, now;
    observer_require_039(!clock_gettime(CLOCK_MONOTONIC, &start), "observer clock");
    unsigned attempts = 0;
    do {
        ++attempts;
        if (samgr_ping_030()) {
            observer_require_039(read_path("/sys/fs/selinux/enforce", enforcing, sizeof(enforcing)) > 0 &&
                                 enforcing[0] == '1', "enforcement after genuine manager reply");
            dprintf(1, "ORIGINAL_INIT039_MANAGER_PING_PASS attempts=%u domain=u:r:init:s0 enforcing=1 genuine_handle0_reply=1 full_services_ready=0 desktop_not_tested=1\n", attempts);
            _exit(0);
        }
        struct timespec interval = {0, 250000000}; nanosleep(&interval, NULL);
        observer_require_039(!clock_gettime(CLOCK_MONOTONIC, &now), "observer deadline clock");
    } while (now.tv_sec - start.tv_sec < 45);
    dprintf(1, "ORIGINAL_INIT039_MANAGER_PING_UNVERIFIED attempts=%u full_services_ready=0\n", attempts);
    _exit(2);
}
