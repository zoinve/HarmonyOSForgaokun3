/* Test-only strict remote-object extraction; no pointer is read before mapping checks. */
#include <linux/android/binder.h>
#include <stdint.h>
#include <string.h>

static int samgr_object_045(const void *mapping, size_t size,
                            const struct binder_transaction_data *tx, uint32_t *handle)
{
    uintptr_t start=(uintptr_t)mapping, data=tx->data.ptr.buffer, offsets=tx->data.ptr.offsets;
    if ((tx->flags & TF_STATUS_CODE) || tx->data_size < sizeof(struct flat_binder_object) ||
        tx->data_size > 65536 || tx->offsets_size != sizeof(binder_size_t) ||
        data < start || data-start > size || tx->data_size > size-(data-start) ||
        offsets < start || offsets-start > size || sizeof(binder_size_t) > size-(offsets-start)) return -1;
    binder_size_t offset;
    memcpy(&offset,(const void *)offsets,sizeof(offset));
    if (offset % 4 || offset > tx->data_size-sizeof(struct flat_binder_object)) return -1;
    struct flat_binder_object object;
    memcpy(&object,(const void *)(data+offset),sizeof(object));
    if (object.hdr.type != BINDER_TYPE_HANDLE || !object.handle) return -1;
    *handle=object.handle;
    return 1;
}
