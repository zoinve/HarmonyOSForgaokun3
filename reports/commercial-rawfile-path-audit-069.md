# Original FindRawFile Filesystem Boundary

This is an offline audit, not an operational 069 boot. No 069 boot exists yet.
Original ELF: /system/lib64/platformsdk/libglobal_resmgr.z.so.
SHA256: 4949c48ada2bbad6ebe7e56ba5499b1f44e28149e17c2ea1cc77517b3d426669.
Binary, symbols and complete disassembly are preserved in
commercial-rawfile-path-audit-069/.

The original exported HapManager::FindRawFile begins at VA 0x41ac4.
Static code at 0x41ba4 copies the candidate resource index path, finds its last
slash at 0x41bbc, then forms its directory prefix. Code at 0x41c28..0x41c60
normalizes an optional rawfile/ prefix. Code at 0x41c94/0x41c98 references
VA 0x23f63, whose exact original bytes are the zero-terminated /resources/.
It appends the normalized filename and calls realpath at 0x41cec.
The null result reaches the observed error branch at 0x41db4.

Original runtime 068 log lines 205798..205827 and 259891..259924 report
FindRawFile path to realpath error immediately before Get rawFile error for
welcome_land_one.mp4 and welcome_land_two.mp4. Both assets are present and
CRC-valid in the supplied original HAP. The warning is not merely inferred
from an empty resource name or from a reference implementation.

The original BMS logs at 39.785..39.810 seconds identify the actual public
module path /data/app/el1/bundle/public/com.huawei.hmos.hwstartupguide/
pc_hwstartupguide, an extraction attempt, missing _tmp rename source and
module-directory deletion. These alone do not prove the final directory state.
Original ArkCompiler subsequently reports the sandbox virtual module path
/data/storage/el1/bundle/pc_hwstartupguide/ets/modules.abc. This also is not a
complete filesystem inventory or proof of a physical extracted file.

Next action: inspect the actual public/preinstall/sandbox resource directory
and stock filesystem lookup conditions. Do not assume which candidate index
path is selected, create package installation records, widen sandbox access,
replace private C++ functions, or label media/desktop success without runtime
evidence. The L410 FindRawFile interposer addresses a similar path boundary,
but this audit neither executes it nor proves it is required on this device.
