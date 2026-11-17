# EGL bridge 024 — isolate internal function binding

023 removed the mapper visibility failure but retained black scanouts. Read-only inspection found that our bridge's `eglGetDisplay` calls `eglGetPlatformDisplayEXT` through its PLT, while the original commercial frontend exports the same name. This permits interposition and may confuse frontend display objects with backend handles.

A small executable ELF characterization reproduced interception by a globally exported frontend function. Relinking with `-Bsymbolic-functions` made the internal call remain local. This fixture is **not** a HarmonyOS runtime or GPU test.

The actual AArch64 commercial bridge was independently relinked using its original source and original commercial runtime libraries. Disassembly confirms the previously indirect self-call now targets the local implementation. Public exports are unchanged; old artifacts and original commercial frontend are untouched. SDK headers/toolchain remain build inputs, not replacement runtime libraries.

New provider: 81,344 bytes, SHA256 `fd60efc04badc014160c52eefa9042ddace3f95cddca72ee9083964a0e533f53`. Build details and old/new disassembly are in `commercial-egl-024/`. This addresses a verified binding hazard, but its role in the physical black screen remains a hypothesis until a separate bounded target test. No desktop success is claimed.
