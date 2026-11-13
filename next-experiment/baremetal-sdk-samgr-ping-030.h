/* Query the genuine context manager; never register a replacement manager. */
#include <sys/mman.h>

static int samgr_ping_030(void)
{
    int fd = open("/dev/binder", O_RDWR | O_CLOEXEC | O_NONBLOCK);
    require(fd >= 0, "open enforcing-policy Binder ping caller");
    const size_t mapping_size = 1024 * 1024;
    void *mapping = mmap(NULL, mapping_size, PROT_READ, MAP_PRIVATE, fd, 0);
    require(mapping != MAP_FAILED, "bounded Binder caller mapping");
    struct binder_transaction_data tx = {.target.handle = 0, .code = 0x5f504e47};
    unsigned char command[4 + sizeof(tx)];
    uint32_t op = BC_TRANSACTION;
    memcpy(command, &op, 4); memcpy(command + 4, &tx, sizeof(tx));
    struct binder_write_read wr = {.write_size = sizeof(command), .write_buffer = (uintptr_t)command};
    require(!ioctl(fd, BINDER_WRITE_READ, &wr) && wr.write_consumed == sizeof(command),
            "send actual context-manager ping transaction");
    int received = 0, result = -1;
    for (unsigned attempt = 0; attempt < 1000 && !received; ++attempt) {
        unsigned char events[8192];
        memset(&wr, 0, sizeof(wr)); wr.read_size = sizeof(events); wr.read_buffer = (uintptr_t)events;
        if (ioctl(fd, BINDER_WRITE_READ, &wr)) {
            require(errno == EAGAIN || errno == EINTR, "nonblocking Binder ping read");
            struct timespec interval = {0, 1000000}; nanosleep(&interval, NULL); continue;
        }
        require(wr.read_consumed <= sizeof(events), "Binder ping event buffer bounds");
        for (size_t pos = 0; pos < wr.read_consumed;) {
            require(wr.read_consumed-pos >= 4, "Binder ping event header");
            memcpy(&op, events + pos, 4); pos += 4;
            size_t size = _IOC_SIZE(op);
            require(size <= wr.read_consumed-pos, "Binder ping event payload bounds");
            if (op == BR_REPLY) {
                require(size == sizeof(tx), "Binder ping reply structure");
                memcpy(&tx, events + pos, sizeof(tx));
                uintptr_t start = (uintptr_t)mapping, buffer = tx.data.ptr.buffer;
                require(buffer >= start && buffer-start <= mapping_size &&
                        tx.data_size <= mapping_size-(buffer-start) && tx.data_size <= 4096,
                        "Binder ping reply lies inside mapped buffer");
                result = 0;
                if (tx.flags & TF_STATUS_CODE) {
                    require(tx.data_size == sizeof(int32_t), "Binder ping status layout");
                    memcpy(&result, (void *)buffer, sizeof(int32_t));
                }
                dprintf(1, "SELINUX030_PING_REPLY uid=%u bytes=%llu flags=%u result=%d\n",
                        tx.sender_euid, (unsigned long long)tx.data_size, tx.flags, result);
                uint32_t free_op = BC_FREE_BUFFER;
                unsigned char release[4 + sizeof(binder_uintptr_t)];
                memcpy(release, &free_op, 4); memcpy(release+4, &tx.data.ptr.buffer, sizeof(binder_uintptr_t));
                struct binder_write_read free_wr = {.write_size=sizeof(release), .write_buffer=(uintptr_t)release};
                require(!ioctl(fd, BINDER_WRITE_READ, &free_wr) && free_wr.write_consumed == sizeof(release),
                        "release actual Binder ping reply");
                received = 1;
            } else if (op == BR_DEAD_REPLY || op == BR_FAILED_REPLY) {
                received = 1; result = -2;
            } else {
                require(op == BR_NOOP || op == BR_TRANSACTION_COMPLETE, "expected Binder ping event");
            }
            pos += size;
        }
    }
    munmap(mapping, mapping_size); close(fd);
    dprintf(1, "SELINUX030_PING_RESULT received=%d result=%d full_services_ready=0\n", received, result);
    return received && result == 0;
}
