#ifndef COMMERCIAL_LINEAR_LAYOUT_074_H
#define COMMERCIAL_LINEAR_LAYOUT_074_H

#include <cstdint>

namespace commercial074 {
constexpr uint64_t MAX_LINEAR_BYTES = UINT64_C(256) * 1024 * 1024;
// GRAPHIC_PIXEL_FMT_BLOB in pinned upstream graphic_surface surface_type.h.
constexpr int32_t BLOB_FORMAT = 38;

inline bool blob(int32_t format) { return format == BLOB_FORMAT; }

inline bool rgb(int32_t format)
{
    return format == PIXEL_FMT_RGBA_8888 || format == PIXEL_FMT_RGBX_8888 ||
        format == PIXEL_FMT_BGRA_8888 || format == PIXEL_FMT_BGRX_8888;
}

inline bool yuv(int32_t format)
{
    return format == PIXEL_FMT_YCBCR_420_SP || format == PIXEL_FMT_YCRCB_420_SP;
}

struct LinearLayout {
    uint32_t plane_count = 0;
    uint32_t chroma_offset = 0;
    uint64_t required_bytes = 0;
};

inline bool dimensions(uint32_t width, uint32_t height, int32_t format)
{
    if (blob(format)) return height == 1 && width && width <= MAX_LINEAR_BYTES;
    if (!width || !height || width > 16384 || height > 16384) return false;
    if (rgb(format)) return uint64_t(width) * height * 4 <= MAX_LINEAR_BYTES;
    return yuv(format) && !(width & 1) && !(height & 1) &&
        uint64_t(width) * height * 3 / 2 <= MAX_LINEAR_BYTES;
}

// Stride is bytes per row; chroma follows every full luma row, including padding.
inline bool layout(uint32_t width, uint32_t height, int32_t format,
                   int64_t stride, uint64_t available, LinearLayout &out)
{
    out = {};
    if (!dimensions(width, height, format) || stride <= 0 ||
        uint64_t(stride) > MAX_LINEAR_BYTES) return false;
    if (blob(format)) {
        if (stride < width || uint64_t(stride) > available) return false;
        out = {1, 0, uint64_t(stride)};
        return true;
    }
    if (rgb(format)) {
        if (stride < int64_t(width) * 4) return false;
        const uint64_t bytes = uint64_t(stride) * height;
        if (bytes > available || bytes > MAX_LINEAR_BYTES) return false;
        out = {1, 0, bytes};
        return true;
    }
    if (stride < width || (stride & 1)) return false;
    const uint64_t luma = uint64_t(stride) * height;
    const uint64_t bytes = luma + uint64_t(stride) * (height / 2);
    if (bytes > available || bytes > MAX_LINEAR_BYTES) return false;
    out = {2, static_cast<uint32_t>(luma), bytes};
    return true;
}

struct AllocationShape {
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t bpp = 0;
};

inline bool allocation_shape(uint32_t width, uint32_t height, int32_t format,
                             bool align512, AllocationShape &out)
{
    out = {};
    if (!dimensions(width, height, format)) return false;
    const uint32_t bytes_per_pixel = rgb(format) ? 4 : 1;
    const uint32_t row_alignment = 512 / bytes_per_pixel;
    const uint32_t allocated_width = align512 ?
        (width + row_alignment - 1) & ~(row_alignment - 1) : width;
    out = {allocated_width, yuv(format) ? height + height / 2 : height,
           bytes_per_pixel * 8};
    return uint64_t(out.width) * out.height * bytes_per_pixel <= MAX_LINEAR_BYTES;
}
}
#endif
