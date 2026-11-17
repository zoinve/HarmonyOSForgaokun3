#ifndef LIVE_DEBUG_ADDRESS_159_H
#define LIVE_DEBUG_ADDRESS_159_H
#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <ifaddrs.h>
#include <net/if.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <sys/stat.h>
#include <unistd.h>

static int live_address159_allowed(const char *address)
{
    struct in_addr value;
    if (inet_pton(AF_INET,address,&value) != 1) return 0;
    unsigned host = ntohl(value.s_addr);
    return (host & 0xffffff00U) == 0xc0a80a00U && (host & 255U) != 0 && (host & 255U) != 255;
}

/* A changed or ambiguous address is absent evidence, not a guessed old lease. */
static int live_address159_select(const struct ifaddrs *head, char address[INET_ADDRSTRLEN])
{
    unsigned scanned = 0, matches = 0;
    address[0] = 0;
    for (; head && scanned < 128; head = head->ifa_next, ++scanned) {
        if (!head->ifa_name || strcmp(head->ifa_name,"wlan0") || !(head->ifa_flags & IFF_UP) ||
            !head->ifa_addr || head->ifa_addr->sa_family != AF_INET) continue;
        char found[INET_ADDRSTRLEN];
        if (!inet_ntop(AF_INET,&((const struct sockaddr_in *)head->ifa_addr)->sin_addr,found,sizeof(found)) ||
            !live_address159_allowed(found)) return -1;
        if (address[0] && strcmp(address,found)) return -1;
        if (!address[0]) { strcpy(address,found); ++matches; }
    }
    return !head && matches == 1 ? 0 : -1;
}

/* Change only our packaged diagnostic listen line, never a host SSH config. */
static int live_address159_config(const char *input, const char *output, const char *address)
{
    if (!live_address159_allowed(address)) return -1;
    int fd = open(input,O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    struct stat metadata;
    if (fd < 0) return -1;
    if (fstat(fd,&metadata) || !S_ISREG(metadata.st_mode) || metadata.st_size < 1 || metadata.st_size > 8192) {
        close(fd); return -1;
    }
    char data[8193], result[8256];
    ssize_t count = pread(fd,data,(size_t)metadata.st_size,0);
    close(fd);
    if (count != metadata.st_size || memchr(data,0,(size_t)count)) return -1;
    data[count] = 0;
    const char *old = "ListenAddress 192.168.10.210\n";
    char *line = strstr(data,old);
    if (!line || (line != data && line[-1] != '\n') || strstr(line + strlen(old),"ListenAddress ")) return -1;
    /* Our canonical template must contain exactly one address directive. */
    unsigned bindings = 0;
    for (const char *start = data; *start;) {
        const char *directive = start;
        while (*directive == ' ' || *directive == '\t') ++directive;
        if (!strncasecmp(directive,"ListenAddress",13) && isspace((unsigned char)directive[13])) {
            if (directive != line) return -1;
            ++bindings;
        }
        const char *next = strchr(start,'\n');
        if (!next) break;
        start = next + 1;
    }
    if (bindings != 1) return -1;
    size_t prefix = (size_t)(line - data);
    memcpy(result,data,prefix);
    int length = snprintf(result + prefix,sizeof(result) - prefix,"ListenAddress %s\n%s",address,line + strlen(old));
    if (length < 0 || (size_t)length >= sizeof(result) - prefix) return -1;
    size_t total = prefix + (size_t)length;
    int out = open(output,O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC,0600);
    if (out < 0) return -1;
    size_t written = 0;
    while (written < total) {
        ssize_t n = write(out,result + written,total - written);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) { close(out); return -1; }
        written += (size_t)n;
    }
    return close(out);
}
#endif
