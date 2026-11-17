# Original PixelMap Warning Audit 067 (Offline Only)

The original /system/lib64/platformsdk/libimage_native.z.so was read directly
from the unchanged supplied system image. SHA256:
c56b30b581b310e587a9eecf7fcaf7606c86af3e13ab6803c313d65a83af1904.
No library execution, instruction patch, module build or operational 067 boot
was performed. Binary, dynamic symbols and disassembly are preserved under
commercial-pixelmap-audit-067.

The exact log string is at file offset 0x8f55. The relevant reference is in
PixelMap::SetMemoryName: adrp/add at VA 0x11b5c4/0x11b5c8 selects 0x8f55;
the log call at 0x11b5f0 follows failed ioctl handling. The ioctl request built
at 0x11b540/0x11b548 is 0x41007701. The retained HarmonyMac ashmem UAPI uses
magic 0x77 and a 256-byte SET_NAME, matching that request rather than proving
an ioctl-number mismatch. Its implementation rejects renaming after backing
creation; actual failing errno has not been captured here.

ImageSource::CreatePixelMap calls SetMemoryName at 0xee574, then examines the
temporary string representation at 0xee578 and continues with the PixelMap.
CreatePixelMapExtended calls it at 0xf00c8 and similarly continues at 0xf00cc.
Neither observed call site tests the SetMemoryName return to reject the image.
Thus repeated naming logs alone do not establish failed pixel allocation or
decoding. This does not prove all original callers or image paths are healthy.

Do not modify ashmem or return fabricated success based on these logs. The
remaining investigation must distinguish missing/invalid original welcome
resources, UI draw content and genuine scene/window behavior. The denied 034
HiDumper requests must not be repeated under forged identities. A future full
scanout capture should preserve actual completed framebuffer pixels, not add
synthetic content or force-stop the original startupguide.
