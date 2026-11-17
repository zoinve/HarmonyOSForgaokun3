#include "display_type.h"
#include "commercial-linear-layout-074.h"
#include <cassert>
#include <climits>
#include <initializer_list>

int main()
{
    using namespace commercial074;
    LinearLayout result;
    AllocationShape shape;
    unsigned cases = 0;
    for (int format : {PIXEL_FMT_YCBCR_420_SP, PIXEL_FMT_YCRCB_420_SP}) {
        for (auto width : {2160U, 2560U, 3120U}) {
            const uint32_t height = width == 3120 ? 2080 : 1440;
            assert(allocation_shape(width, height, format, false, shape));
            assert(shape.width == width && shape.height == height * 3 / 2 && shape.bpp == 8);
            const uint32_t pitch = (width + 63) & ~63U;
            const uint64_t bytes = uint64_t(pitch) * height * 3 / 2;
            assert(layout(width, height, format, pitch, bytes, result));
            assert(result.plane_count == 2 && result.chroma_offset == pitch * height);
            assert(result.required_bytes == bytes);
            assert(!layout(width, height, format, pitch, bytes - 1, result));
            assert(result.plane_count == 0 && result.required_bytes == 0);
            assert(allocation_shape(width, height, format, true, shape));
            assert(shape.width >= width && !(shape.width % 512));
            ++cases;
        }
        assert(!dimensions(1, 2, format));
        assert(!dimensions(2, 1, format));
        assert(!dimensions(0, 2, format));
        assert(!dimensions(16386, 2, format));
        assert(!layout(2, 2, format, 1, 6, result));
        assert(!layout(2, 2, format, 3, 9, result));
        assert(!layout(2, 2, format, INT64_MAX, UINT64_MAX, result));
        assert(!layout(2, 2, format, -1, UINT64_MAX, result));
        assert(!layout(16384, 16384, format, 16384, UINT64_MAX, result));
    }
    for (int format : {PIXEL_FMT_RGBA_8888, PIXEL_FMT_RGBX_8888,
                       PIXEL_FMT_BGRA_8888, PIXEL_FMT_BGRX_8888}) {
        assert(allocation_shape(2560, 1600, format, false, shape));
        assert(shape.width == 2560 && shape.height == 1600 && shape.bpp == 32);
        assert(layout(2560, 1600, format, 10240, 16384000, result));
        assert(result.plane_count == 1 && result.required_bytes == 16384000);
        assert(!layout(2560, 1600, format, 10239, 16384000, result));
        assert(!layout(2560, 1600, format, 10240, 16383999, result));
        ++cases;
    }
    assert(dimensions(262160, 1, BLOB_FORMAT));
    assert(allocation_shape(262160, 1, BLOB_FORMAT, false, shape));
    assert(shape.width == 262160 && shape.height == 1 && shape.bpp == 8);
    assert(layout(262160, 1, BLOB_FORMAT, 262208, 266240, result));
    assert(result.plane_count == 1 && result.required_bytes == 262208);
    assert(!layout(262160, 1, BLOB_FORMAT, 262208, 262207, result));
    assert(!dimensions(UINT32_MAX, 1, BLOB_FORMAT));
    assert(!dimensions(2, 2, 38));
    assert(!dimensions(2, 2, 37));
    assert(cases == 10);
    return 0;
}
