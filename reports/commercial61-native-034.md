# Commercial 034 — original RenderService tree and screen observations

033 observed matching original GLES frontend and Mesa public states, including late observations after SceneBoard node creation. The real scanout and its client target remained black. This does not justify replacing GL dispatch or weakening original service checks. The next boundary is the original RenderService's actual display-root tree, node bounds, visibility and screen state.

034 asks the original `/system/bin/hidumper` for service 10's `screen` and `MultiRSTrees` diagnostics once at observer sample 10 (nominally about 55 seconds). Each client inherits the existing three-second command timeout; statuses and begin/end markers are captured in the existing evidence stream. Killing a client need not cancel an already queued service-side task. Dumping can affect timing and is not perfectly side-effect-free. In the release source, `MultiRSTrees` does not force a single-frame render, unlike `RSTree`.

Command provenance: OpenHarmony-6.0-Release `rosen/modules/render_service_base/include/gfx/dump/rs_dump_manager.h` maps these exact query names to screen and multi-tree dump callbacks. The actual commercial image's `librender_service_base.z.so` contains both exact UTF-16 command strings and matching help descriptions. The original image contains `/system/bin/hidumper`; the official HiDumper README documents `-s <service> -a <arguments>`. Upstream source is supporting evidence, not a claim of binary identity. No tree mutation commands, synthetic nodes, forced success, logging switches or GPU initialization commands are requested.

The 033 EGL provider, 030 composer provider and 032 ordinary launcher retry remain unchanged. Only the diagnostic bootstrap observation changes. No SDK runtime substitution, original image writes, permission bypass, service identity changes or authentication/sandbox modifications. All three adaptation references remain the baseline. Actual original desktop pixels remain the acceptance criterion before WiFi/touch/USB/video-output work.

Tests exercise the exact query helper and verify that removing its helper and single call recovers the 033 bootstrap byte-for-byte. They are host fixtures, not target RS evidence. Target results are pending. Strict trusted SSH, Ubuntu default/manual entry, original image hashes, enabled/active screen-off timer, memory admission and unchanged 90-second target / 210-second outer software deadlines remain required. Software deadlines cannot guarantee recovery from a kernel/hardware hang.

## Offline verification

All 22 scoped offline regressions passed, including exact query arguments/sample gating, bootstrap source recovery, prior compiled GL state/readback fixtures and real child timeout/RAM checks. All five assembled workflows passed syntax, candidate, trusted-address and screen-off guard checks. The historical operational collection was not rerun.

The bootstrap is 852,392 bytes, SHA256 `74d4c6c778168877225a4a506acb2bffa9cf208b24b5ccb4c3661428d1c4868c`. The final overlay is 773,692 bytes, SHA256 `39234daab6f38fbe7eead2cdddca471336bba6c1aa32dee7d0be8d8c0252bc33`; ordered 001 → 017 → 016 → 034 extraction matches the complete build byte-for-byte and mode-for-mode with parent directories in place. The rendering providers and launcher are unchanged. These results do not verify target tree content or a genuine desktop.

## Installation

Installation preserved all 132 existing EFI files. Both non-PID1 execution guards refused with exit 77; EFI free space was 218,005,504 bytes. Ubuntu default, the manual entry and enabled screen-off timer were preserved. Installation selected no one-shot entry and requested no reboot. A separate single bounded 034 run has been launched; runtime evidence is pending.

## Actual result (closed)

The single run completed on November 13 UTC (November 14 local), 18:37:40–18:40:32. All 59 retrieved files matched their remote hashes; retrieval used read-only, no-journal-replay access and unmounted the evidence partition. Configured target termination was observed. SceneBoard was installed and running, but all three real 160×256 exports remained black. The latest synchronized compositor observation at guest 73.531 seconds found both actual client input and completed output black. No genuine desktop is verified.

Neither requested RS dump returned tree or screen content. Both clients exited 255 (raw wait status 65280), not a timeout. The original HiDumper service explicitly rejected observer UID 0 with `No dump permission` at guest 55.220 and 55.320 seconds. SELinux was permissive; this separate native permission check remained effective and was not bypassed. See `tree-query-analysis.json` for raw-derived statuses, permission evidence and deduplicated frame records.

Existing ordinary logs do show the desktop's requested 2560×1600 bounds and wallpaper bounds of 2560×1706.67, followed by both scenes becoming visible at 47.502 seconds. These are application/window-manager observations, not a substitute for the denied RS tree dump or evidence of rendered pixels. Worker-thread JavaScript exceptions likewise do not establish that the main SceneBoard scene failed; no globals or application state were patched.

Post-return verification passed: standard Ubuntu boot `9a9d68a3-f150-4280-9fed-21de5535332f`, current/default entry, firmware, manual entry, all four original commercial image hashes, unmounted evidence partition and enabled/active screen-off timer. Of 132 earlier EFI files, only the legitimate boot-managed random seed changed. This operational attempt is closed; its numbered logs and JSON must not be overwritten or rerun.
