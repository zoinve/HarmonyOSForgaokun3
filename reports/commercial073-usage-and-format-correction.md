# 073 interpretation correction

The raw evidence and allocator-analysis.json are unchanged and correct.
The manually written 073 closure table mistakenly prefixed decimal usage values
with `0x`. Read those cells using this correction:

| JSON decimal | Actual public request hexadecimal |
| --- | --- |
| 1800 | 0x708 |
| 1035 | 0x40b |
| 43 | 0x2b |

In particular, the observed NV12/NV21 allocator requests use 0x40b, not 0x1035.
Do not confuse upstream hilog's separately formatted usage messages with these
direct allocator arguments. This changes no captured request or pixel result.

Additional source verification for the next implementation identifies format
38 as GRAPHIC_PIXEL_FMT_BLOB in pinned upstream graphic_surface surface_type.h.
The 262160x1 request is a byte-buffer geometry, not an oversized image.
It needs genuine byte-backed allocation/mapping, but must not be imported into
EGL as an RGB image or assigned a fabricated pixel format.

The additional upstream references supplement, not replace, the original three
required references. See the 074 source/design report for exact pinned commits.
