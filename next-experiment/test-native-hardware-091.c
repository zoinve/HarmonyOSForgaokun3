#define HARDWARE091_TEST
#include "native-hardware-091.c"
#include <assert.h>
#include <stdio.h>

int main(void)
{
    struct identity091_facts f = {0, 1, 0, 1, 1, 0, 0};
    assert(identity091_decide(f) == ID091_SUPPLY_SERIAL);
    f.serial_present = f.serial_match = 1;
    assert(identity091_decide(f) == ID091_ORIGINAL_MODULE);
    f.serial_match = 0;
    assert(identity091_decide(f) == ID091_SERIAL_CONFLICT);
    f.metadata_match = 0;
    assert(identity091_decide(f) == ID091_METADATA_CONFLICT);
    f.hardware_ok = 0;
    assert(identity091_decide(f) == ID091_HARDWARE_ERROR);
    f.existing_nonempty = 1;
    assert(identity091_decide(f) == ID091_EXISTING_INVALID);
    f.api_ok = 0;
    assert(identity091_decide(f) == ID091_API_ERROR);
    f.existing_valid = 1;
    assert(identity091_decide(f) == ID091_PRESERVE);
    puts("8 identity decision scenarios PASS; no original API mocked or target code executed");
    return 0;
}
