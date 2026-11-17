"""Original MHI/QRTR transport plus bounded read-only late kernel evidence."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-080.py'))
inner = p['inner']
LOGGER = r'''
static void network081_kmsg(void)
{
    static int fd = -1;
    unsigned records = 0, bytes = 0, selected = 0, losses = 0;
    int error = 0;
    if (fd < 0) {
        fd = open("/dev/kmsg", O_RDONLY | O_NONBLOCK | O_CLOEXEC);
        if (fd < 0) {
            dprintf(1, "NETWORK081_KMSG_OPEN_FAILED errno=%d\n", errno);
            return;
        }
    }
    while (records < 512 && bytes < 131072) {
        char text[8193];
        ssize_t n = read(fd, text, sizeof(text) - 1);
        if (n < 0) {
            if (errno == EPIPE && ++losses <= 4) continue;
            error = errno;
            break;
        }
        if (!n) break;
        text[n] = 0;
        ++records;
        bytes += (unsigned)n;
        if (strstr(text, "ath11k") || strstr(text, "mhi") ||
            strstr(text, "qrtr") || strstr(text, "firmware") ||
            strstr(text, "wcn6855")) {
            dprintf(1, "NETWORK081_KMSG_RECORD bytes=%zd\n%.*s\n", n, (int)n, text);
            ++selected;
        }
    }
    dprintf(1, "NETWORK081_KMSG_DRAIN records=%u bytes=%u selected=%u losses=%u errno=%d complete_not_inferred=1\n",
            records, bytes, selected, losses, error);
}
'''
NETIFS = r'''
static void network081_netifs(void)
{
    DIR *dir = opendir("/sys/class/net");
    if (!dir) {
        dprintf(1, "NETWORK081_NETIF_OPEN_FAILED errno=%d\n", errno);
        return;
    }
    struct dirent *entry;
    unsigned count = 0;
    while ((entry = readdir(dir)) && count < 32) {
        if (entry->d_name[0] == '.') continue;
        ++count;
        char path[512], target[512], state[128];
        snprintf(path, sizeof(path), "/sys/class/net/%s/operstate", entry->d_name);
        if (read_text(path, state, sizeof(state))) strcpy(state, "unreadable");
        dprintf(1, "NETWORK081_NETIF name=%s operstate=%s\n", entry->d_name, state);
        snprintf(path, sizeof(path), "/sys/class/net/%s/phy80211", entry->d_name);
        ssize_t n = readlink(path, target, sizeof(target));
        if (n > 0)
            dprintf(1, "NETWORK081_PHY_LINK name=%s target=%.*s connectivity_not_inferred=1\n",
                    entry->d_name, (int)n, target);
    }
    closedir(dir);
}
'''
outer = p['outer'].replace('commercial61-native-080', 'commercial61-native-081').replace('COMMERCIAL080', 'COMMERCIAL081')
outer = outer.replace('wifi-power080', 'wifi-power081').replace('wifi-pci-power080', 'wifi-pci-power081').replace(
    'wifi-driver080', 'wifi-driver081').replace('wifi-observation080', 'wifi-observation081').replace('NETWORK080', 'NETWORK081')
anchor = '                char *wifi080[] = '
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '''                char *qrtr081[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "qrtr_mhi", NULL};
                (void)probe("wifi-qrtr081", qrtr081, 8);
''' + anchor, 1)
anchor = 'static void native_diagnostics(pid_t child)\n{'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, LOGGER + NETIFS + '\n' + anchor + '\n    network081_kmsg();\n    network081_netifs();', 1)
anchor = '                native_original();'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '                network081_kmsg();\n                network081_netifs();\n' + anchor, 1)
anchor = '"for d in /sys/bus/pci/devices/* /sys/bus/platform/devices/*pcie* "'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '"for d in /sys/bus/mhi/devices/* /sys/bus/pci/devices/* /sys/bus/platform/devices/*pcie* "', 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace(
    'commercial61-native-080', 'commercial61-native-081')

if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
