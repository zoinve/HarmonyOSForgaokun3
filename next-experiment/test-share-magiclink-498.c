#include <assert.h>
#include <stdio.h>
#include "share-magiclink-497.h"

static int parse(const char *text)
{
    char buffer[256];
    struct share497_request request;
    assert(strlen(text) < sizeof(buffer));
    strcpy(buffer, text);
    return share497_parse(buffer, &request);
}

int main(void)
{
    const char *valid = "4449524543542d74657374\n02:00:00:00:00:01\n\x22test-only-key\x22\n2412\n0";
    assert(!parse(valid));
    assert(!parse("00\n02:00:00:00:00:01\n0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n5180\n0"));
    assert(parse("0\n02:00:00:00:00:01\n\x22test-only-key\x22\n2412\n0"));
    assert(parse("gg\n02:00:00:00:00:01\n\x22test-only-key\x22\n2412\n0"));
    assert(parse("00\n02:00:00:00:00:xx\n\x22test-only-key\x22\n2412\n0"));
    assert(parse("00\n02:00:00:00:00:01\n\x22short\x22\n2412\n0"));
    assert(parse("00\n02:00:00:00:00:01\n\x22test-only-key\x22\n9999\n0"));
    assert(parse("00\n02:00:00:00:00:01\n\x22test-only-key\x22\n2412\n1"));
    assert(parse("00\n02:00:00:00:00:01\n\x22test-only-key\x22\n2412\n0\nextra"));
    assert(parse("missing-fields"));
    puts("SHARE498 lexical fixtures passed; no radio or handshake acceptance");
    return 0;
}
