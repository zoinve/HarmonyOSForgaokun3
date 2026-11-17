# Commercial desktop investigation: 006

006 corrects the two observer-copy paths that caused 005 to abort before commercial init. It retains the original commercial system, service credentials, original HDF configuration import, RenderService log-directory repair and bounded automatic return. No SDK system services or graphics binaries are introduced.

The single bounded attempt returned to Ubuntu at 09:11:19 UTC on 2026-11-13 (boot ID `8c60eb2d-9f92-4a2d-b802-9c2c9d00c7f1`). All 67 retrieved files match their remote hashes; the original evidence partition was mounted read-only without journal replay and then unmounted. SA 511 remains unsupported and SceneBoard dependency installation still fails. A working desktop was **not** obtained.

The new observer produced no profile log. Its code silently executes original samgr if opening its private log fails; therefore neither successful execution of the observer nor any runtime config-policy result has been established. The original samgr itself ran as UID 5555. Candidate archive inspection confirms the changed service path and unchanged remaining credentials/config fields, but does not prove which configuration the running init consumed. Further diagnostics must establish observer entry, log-open errors and the merged configuration before attributing the missing profiles to a specific path or permission.

## Graphics interface finding

The original commercial composer service is version 1.3. Although its vendor implementation also contains C++ classes, actual `LoadVdiFuncPart1` disassembly calls `dlsym` for C functions including `RegHotPlugCallback`, `GetDisplayCapability`, `GetDisplaySupportedModes`, `GetDisplayMode`, `SetDisplayMode` and power/backlight operations. Therefore the presence of vendor C++ classes alone does **not** prove that a wholly new C++ adapter is required. Any MateBook implementation still needs verified structure layouts, required exports, original commercial loader compatibility and actual original-service execution; copying a version-7 service or declaring ABI compatibility from symbol names is not acceptable.

Ubuntu remains the default. The user-disabled forced-screen-off timer must remain disabled. Original commercial images and all earlier numbered evidence are preserved.
