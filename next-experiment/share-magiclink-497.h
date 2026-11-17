/* Strict lexical parsing only; authentication remains in upstream supplicant. */
#ifndef SHARE_MAGICLINK_497_H
#define SHARE_MAGICLINK_497_H
#include <stddef.h>
#include <string.h>

struct share497_request {
    char *ssid_hex, *bssid, *key;
    int frequency;
};

static int share497_hex(char c)
{
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') ||
           (c >= 'A' && c <= 'F');
}

static int share497_parse(char *text, struct share497_request *out)
{
    char *field[5];
    size_t n, i;
    int frequency = 0;
    if (!text || !out || strlen(text) > 200) return -1;
    field[0] = text;
    for (i = 0; i < 4; ++i) {
        char *end = strchr(field[i], '\n');
        if (!end) return -1;
        *end = 0;
        field[i + 1] = end + 1;
    }
    if (strchr(field[4], '\n') || strcmp(field[4], "0")) return -1;
    n = strlen(field[0]);
    if (n < 2 || n > 64 || n % 2) return -1;
    for (i = 0; i < n; ++i) if (!share497_hex(field[0][i])) return -1;
    if (strlen(field[1]) != 17) return -1;
    for (i = 0; i < 17; ++i)
        if (i % 3 == 2 ? field[1][i] != ':' : !share497_hex(field[1][i])) return -1;
    n = strlen(field[2]);
    if (n == 64 && field[2][0] != '"') {
        for (i = 0; i < n; ++i) if (!share497_hex(field[2][i])) return -1;
    } else {
        if (n < 10 || n > 65 || field[2][0] != '"' || field[2][n - 1] != '"') return -1;
        for (i = 1; i < n - 1; ++i)
            if ((unsigned char)field[2][i] < 32 || (unsigned char)field[2][i] > 126) return -1;
    }
    if (strlen(field[3]) != 4) return -1;
    for (i = 0; i < 4; ++i) {
        if (field[3][i] < '0' || field[3][i] > '9') return -1;
        frequency = frequency * 10 + field[3][i] - '0';
    }
    if (frequency < 2412 || frequency > 5900) return -1;
    out->ssid_hex = field[0];
    out->bssid = field[1];
    out->key = field[2];
    out->frequency = frequency;
    return 0;
}
#endif
