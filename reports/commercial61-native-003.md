# Commercial 003: corrected passive diagnostics

003 changes diagnostic descriptor ownership only; the functional log-directory repair from 002 is unchanged. A private close-on-exec descriptor is duplicated before the continuous collector closes its original descriptors, inherited by passive observers, and closed in the parent before executing commercial init. A real fork/exec test reproduced the 002 failure and passed with this correction.

The single bounded test returned to Ubuntu on 2026-11-13 at 08:17:34 UTC, boot ID `d19c767e-7491-4a68-b68b-0ee61cc6db72`. All 67 retrieved evidence files match their remote hashes. Retrieval used `ro,noload,nodev,nosuid,noexec` and unmounted the original LAB partition afterwards; no journal replay was performed.

## Actual findings

- Original commercial init executes, and original `/system/bin/render_service` remains present across the sampled interval. This is process execution, not renderer readiness or desktop acceptance.
- 3,433 early kernel records and 47 RenderService log snapshots were retained. The original dynamic loader resolves the original HDF manager's dependencies successfully. Commercial internal directory names such as `chipset-sdk` do not mean that SDK 7 files were substituted.
- Init explicitly reports missing `/vendor/etc/init.matebookego.cfg`. The original vendor HDF service definition exists, but no HDF manager process or successful SA 5100 publication is established. A missing board-level import is the next hypothesis to test, not a confirmed repair.
- The original RenderService log identifies the supplied L410 Mali Vulkan ICD, followed by `Failed creating base context during opening of kernel driver.` and `[mali] Kernel module may not have been loaded`. This establishes a hardware-backend mismatch: the MateBook's GPU is FD690, not Kirin Mali. Loading a Mali kernel module or fabricating GPU success is not a valid adaptation.
- The supplied image itself contains L410 launch/preload compatibility hooks. These are original image content, not new changes made by this project. Their presence is not a reason to add identity spoofing or suppress service checks.

SELinux remains supported and permissive (48 observed mode-zero samples), not disabled. Original init, service identities, libraries, images and launchers are unchanged. No SDK userland was substituted. The default Ubuntu entry, manual GPU entry and persistently disabled experimental screen-off timer are retained.

A working commercial desktop is **not obtained**. See `commercial61-native-003/minimal-startup-analysis.json`, `diagnostic-context.txt` and the preserved raw evidence. 004 independently tests one additive MateBook board configuration importing the existing original HDF manager definition; it does not replace the Mali graphics backend.
