#ifndef PERSISTENT_RUNTIME_166_H
#define PERSISTENT_RUNTIME_166_H

static void persistent_runtime166(void)
{
    struct statfs fs;
    struct stat block, data;
    char command[8192], boot[80], previous[80];
    if (read_path("/proc/cmdline",command,sizeof(command)) <= 0 ||
        !option(command,"harmony.persistent_data166=1")) fail("persistent data optin");
    if (stat("/dev/loop3",&block) || stat("/data",&data) || data.st_dev != block.st_rdev ||
        statfs("/data",&fs) || fs.f_type != 0xef53 || fs.f_bsize != 4096 ||
        (unsigned long long)fs.f_blocks*fs.f_bsize < 7516192768ULL ||
        (unsigned long long)fs.f_bavail*fs.f_bsize < 1073741824ULL)
        fail("persistent data mount identity or space");
    if (read_path("/proc/sys/kernel/random/boot_id",boot,sizeof(boot)) != 37 || boot[36] != '\n')
        fail("persistent boot identity");
    boot[36] = 0;
    for (unsigned i=0;i<36;++i)
        if ((i==8 || i==13 || i==18 || i==23) ? boot[i]!='-' :
            !((boot[i]>='0' && boot[i]<='9') || (boot[i]>='a' && boot[i]<='f')))
            fail("persistent boot identity format");
    directory("/data/.harmony-persistent166",0700);
    int root = open("/data/.harmony-persistent166",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    if (root < 0) fail("persistent marker directory");
    int old = openat(root,"last-boot",O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
    int prior = 0;
    if (old >= 0) {
        struct stat st;
        if (fstat(old,&st) || !S_ISREG(st.st_mode) || st.st_uid || st.st_size != 37 ||
            read(old,previous,sizeof(previous)) != 37 || close(old)) fail("persistent prior marker");
        previous[37] = 0;
        if (previous[36] != '\n' || !strncmp(previous,boot,36)) fail("persistent prior boot mismatch");
        for (unsigned i=0;i<36;++i)
            if ((i==8 || i==13 || i==18 || i==23) ? previous[i]!='-' :
                !((previous[i]>='0' && previous[i]<='9') || (previous[i]>='a' && previous[i]<='f')))
                fail("persistent prior identity format");
        prior = 1;
    } else if (errno != ENOENT) fail("persistent prior marker open");
    /* Preserve only adaptation-owned per-boot diagnostic objects. App data and
     * original service configuration are never removed or reset here. */
    if (mkdirat(root,boot,0700)) fail("persistent unique history");
    int history = openat(root,boot,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    int datadir = open("/data",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    if (history < 0 || datadir < 0) fail("persistent history open");
    const char *owned[]={"native-perf-023.trace","native-scanout-013.ppm","native-allocator-073.trace",
        "native-full-068","native-full-075"};
    unsigned archived = 0;
    for (unsigned i=0;i<sizeof(owned)/sizeof(owned[0]);++i) {
        struct stat st;
        if (fstatat(datadir,owned[i],&st,AT_SYMLINK_NOFOLLOW)) {
            if (errno == ENOENT) continue;
            fail("persistent history stat");
        }
        if ((i<3 && !S_ISREG(st.st_mode)) || (i>=3 && !S_ISDIR(st.st_mode)) ||
            renameat(datadir,owned[i],history,owned[i])) fail("persistent history archive");
        ++archived;
    }
    if (fsync(history) || close(history) || fsync(datadir) || close(datadir)) fail("persistent history sync");
    int marker=openat(root,"last-boot.next",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    boot[36]='\n';
    if (marker<0 || write(marker,boot,37)!=37 || fsync(marker) || close(marker) ||
        renameat(root,"last-boot.next",root,"last-boot") || fsync(root) || syncfs(root) || close(root))
        fail("persistent marker commit");
    boot[36]=0;
    if (prior) previous[36]=0;
    dprintf(1,"PERSISTENT166_RUNTIME disk_backed=1 seed_reset=0 boot=%s previous_present=%d previous=%s archived=%u\n",
        boot,prior,prior?previous:"none",archived);
}
#endif
