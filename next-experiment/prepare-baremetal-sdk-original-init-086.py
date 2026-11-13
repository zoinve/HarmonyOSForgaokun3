"""Guest-only syscall logging: never replace a receiver or change permissions."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-085.py')))
source = parent['source'].replace('ORIGINAL_INIT085_', 'ORIGINAL_INIT086_').replace('GRAPHICS085_', 'GRAPHICS086_')
source = source.replace('graphics_profile_events_085', 'graphics_profile_events_086')
assert source.count('#define _GNU_SOURCE\n') == 1
source = source.replace('#define _GNU_SOURCE\n', '#define _GNU_SOURCE\n#include <linux/audit.h>\n#include <linux/netlink.h>\n#include <sys/socket.h>\n#include <sys/time.h>\n', 1)
helper = r'''
/* Linux AArch64 syscall audit, original SAMGR uid only. No permission rules. */
static void graphics_audit_rule_086(void)
{
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_AUDIT);
    if (fd < 0) {
        dprintf(1, "GRAPHICS086_AUDIT_SETUP stage=socket errno=%d\n", errno);
        return;
    }
    struct timeval limit = {.tv_sec = 2};
    struct sockaddr_nl local = {.nl_family = AF_NETLINK};
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &limit, sizeof(limit)) ||
        bind(fd, (struct sockaddr *)&local, sizeof(local))) {
        dprintf(1, "GRAPHICS086_AUDIT_SETUP stage=bind_timeout errno=%d\n", errno);
        close(fd);
        return;
    }
    struct {
        struct nlmsghdr header;
        struct audit_rule_data rule;
    } request;
    memset(&request, 0, sizeof(request));
    request.header.nlmsg_len = NLMSG_LENGTH(sizeof(request.rule));
    request.header.nlmsg_type = AUDIT_ADD_RULE;
    request.header.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
    request.header.nlmsg_seq = 86;
    request.rule.flags = AUDIT_FILTER_EXIT;
    request.rule.action = AUDIT_ALWAYS;
    request.rule.field_count = 2;
    request.rule.fields[0] = AUDIT_ARCH;
    request.rule.values[0] = AUDIT_ARCH_AARCH64;
    request.rule.fieldflags[0] = AUDIT_EQUAL;
    request.rule.fields[1] = AUDIT_UID;
    request.rule.values[1] = 5555;
    request.rule.fieldflags[1] = AUDIT_EQUAL;
    const unsigned calls[] = {SYS_openat, SYS_getdents64, SYS_faccessat};
    for (unsigned i = 0; i < sizeof(calls) / sizeof(calls[0]); ++i)
        request.rule.mask[calls[i] / 32] |= 1U << (calls[i] % 32);
    struct sockaddr_nl kernel = {.nl_family = AF_NETLINK};
    ssize_t sent = sendto(fd, &request, request.header.nlmsg_len, 0,
                          (struct sockaddr *)&kernel, sizeof(kernel));
    if (sent != (ssize_t)request.header.nlmsg_len) {
        dprintf(1, "GRAPHICS086_AUDIT_SETUP stage=send bytes=%ld errno=%d\n", (long)sent, errno);
        close(fd);
        return;
    }
    unsigned char reply[4096] __attribute__((aligned(8)));
    ssize_t got = recv(fd, reply, sizeof(reply), 0);
    if (got >= (ssize_t)NLMSG_LENGTH(sizeof(struct nlmsgerr))) {
        struct nlmsghdr *header = (struct nlmsghdr *)reply;
        if (header->nlmsg_type == NLMSG_ERROR && header->nlmsg_seq == 86) {
            struct nlmsgerr *ack = (struct nlmsgerr *)NLMSG_DATA(header);
            dprintf(1, "GRAPHICS086_AUDIT_ACK error=%d uid=5555 arch=aarch64 calls=openat,getdents64,faccessat receiver_unchanged=1\n", ack->error);
        } else {
            dprintf(1, "GRAPHICS086_AUDIT_SETUP stage=unexpected_reply type=%u seq=%u\n", header->nlmsg_type, header->nlmsg_seq);
        }
    } else {
        dprintf(1, "GRAPHICS086_AUDIT_SETUP stage=receive bytes=%ld errno=%d\n", (long)got, got < 0 ? errno : 0);
    }
    close(fd);
}

'''
assert source.count('int main(void)') == 1
source = source.replace('int main(void)', helper + 'int main(void)')
anchor = '    graphics_profile_events_086();'
assert source.count(anchor) == 1
source = source.replace(anchor, '    graphics_audit_rule_086();\n' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-085', 'baremetal-sdk-original-init-086')
compile(payload, 'original-samgr-syscalls-086-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
