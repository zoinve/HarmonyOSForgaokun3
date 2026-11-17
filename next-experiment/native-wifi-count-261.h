#include <stddef.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/un.h>

static int radio261_bss_count(void)
{
    static const char path[] = "/data/local/tmp/wpa_ctrl/wlan0";
    struct stat node;
    if (lstat(path, &node) || !S_ISSOCK(node.st_mode) || node.st_uid != 0) return 90;
    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return 91;
    struct sockaddr_un client = {.sun_family = AF_UNIX};
    int length = snprintf(client.sun_path + 1, sizeof(client.sun_path) - 1,
                          "matebook_scan_count261_%ld", (long)getpid());
    if (length < 0 || (size_t)length >= sizeof(client.sun_path) - 1) goto fail;
    if (bind(fd, (struct sockaddr *)&client,
             (socklen_t)(offsetof(struct sockaddr_un, sun_path) + 1 + length))) goto fail;
    struct timeval timeout = {.tv_sec = 2};
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) ||
        setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout))) goto fail;
    struct sockaddr_un server = {.sun_family = AF_UNIX};
    memcpy(server.sun_path, path, sizeof(path));
    if (connect(fd, (struct sockaddr *)&server,
                offsetof(struct sockaddr_un, sun_path) + sizeof(path))) goto fail;
    static const char command[] = "SCAN_RESULTS";
    if (send(fd, command, sizeof(command)-1, MSG_NOSIGNAL) != sizeof(command)-1) goto fail;
    char buffer[65536];
    ssize_t bytes = recv(fd, buffer, sizeof(buffer)-1, MSG_TRUNC);
    if (bytes <= 0 || (size_t)bytes >= sizeof(buffer)-1 || memchr(buffer, 0, (size_t)bytes)) goto fail;
    buffer[bytes] = 0;
    static const char header[] = "bssid / frequency / signal level / flags / ssid\n";
    if ((size_t)bytes < sizeof(header)-1 || memcmp(buffer, header, sizeof(header)-1)) goto fail;
    unsigned count = 0;
    char *line = buffer + sizeof(header)-1;
    while (*line) {
        char *end = strchr(line, '\n');
        if (!end) goto fail;
        unsigned tabs = 0;
        for (char *p = line; p < end; ++p) if (*p == '\t') ++tabs;
        if (tabs < 4) goto fail;
        ++count;
        line = end+1;
    }
    close(fd);
    dprintf(1, "RADIO261_SCAN_RESULTS bss_count=%u raw_ssid_and_bssid_exported=0 ui_acceptance_not_inferred=1\n", count);
    return 0;
fail:
    {
        int saved = errno;
        close(fd);
        dprintf(1, "RADIO261_SCAN_RESULTS unavailable=1 errno=%d raw_values_exported=0\n", saved);
        return 92;
    }
}
