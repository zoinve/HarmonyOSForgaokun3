#define BINDER_OBSERVER043_TEST
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <vector>
#include "commercial-binder-observer-043.h"

int main()
{
    static_assert(sizeof(binder_transaction_data) == 64, "Require the matching 64-bit Binder UAPI");
    const char *name = "ohos.rosen.RenderServiceConnection";
    uint32_t length = strlen(name), policy = 0x100;
    std::vector<unsigned char> parcel(12 + (length + 1) * 2 + 16, 0);
    memcpy(parcel.data(), &policy, 4);
    memcpy(parcel.data() + 8, &length, 4);
    for (unsigned i = 0; i < length; ++i) parcel[12 + i * 2] = name[i];
    assert(interface043(parcel.data(), parcel.size()) == 1);
    assert(!interface043(parcel.data(), 8));
    assert(!interface043(parcel.data(), 12 + length * 2));
    parcel[13] = 1;
    assert(!interface043(parcel.data(), parcel.size()));
    parcel[13] = 0;
    parcel[0] = 1;
    assert(!interface043(parcel.data(), parcel.size()));
    parcel[0] = 0;
    auto untouched = parcel;
    binder_transaction_data transaction = {};
    transaction.target.handle = 42;
    transaction.code = 17;
    transaction.flags = TF_ONE_WAY;
    transaction.data_size = parcel.size();
    transaction.data.ptr.buffer = reinterpret_cast<uintptr_t>(parcel.data());
    std::vector<unsigned char> stream(4 + sizeof(transaction));
    uint32_t command = BC_TRANSACTION;
    memcpy(stream.data(), &command, 4);
    memcpy(stream.data() + 4, &transaction, sizeof(transaction));
    auto original = stream;
    binder_write_read request = {};
    request.write_buffer = reinterpret_cast<uintptr_t>(stream.data());
    request.write_size = stream.size();
    BinderSnapshot043 snapshot[2] = {};
    assert(snapshots043(request, snapshot, 2) == 1);
    assert(snapshot[0].interface == 1 && snapshot[0].code == 17);
    assert(snapshot[0].handle == 42 && snapshot[0].flags == TF_ONE_WAY);
    assert(snapshot[0].end == stream.size());
    assert(stream == original && parcel == untouched);
    assert(!snapshots043(request, snapshot, 0));
    request.write_consumed = request.write_size;
    assert(!snapshots043(request, snapshot, 2));
    request.write_consumed = 0;
    request.write_size -= 1;
    assert(!snapshots043(request, snapshot, 2));
    request.write_size = 65537;
    assert(!snapshots043(request, snapshot, 2));
    binder_transaction_data_sg scatter = {};
    scatter.transaction_data = transaction;
    stream.resize(4 + sizeof(scatter));
    command = BC_TRANSACTION_SG;
    memcpy(stream.data(), &command, 4);
    memcpy(stream.data() + 4, &scatter, sizeof(scatter));
    request.write_buffer = reinterpret_cast<uintptr_t>(stream.data());
    request.write_size = stream.size();
    assert(snapshots043(request, snapshot, 2) == 1);
    command = BC_REPLY_SG;
    memcpy(stream.data(), &command, 4);
    assert(!snapshots043(request, snapshot, 2));
    return 0;
}
