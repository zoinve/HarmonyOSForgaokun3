# Native 074: OOBE Reached, Desktop Not Verified

Run `commercial61-native-074-4e2b7000-0021-4ea6-af3a-5189eb44499a`,
2026-11-15 01:57:46 to 02:01:53 UTC. One native attempt only.

The device returned to Ubuntu, boot ID
`675a916f-a7a1-4236-92a8-62c6e4fa5fc3`. The read-only/noload retrieval
authenticated all 64 files. Post-return verification confirmed Ubuntu current
and default, unchanged firmware and all four original images, enabled/active
screen-off timer, preserved manual entry and unmounted LAB partition.

The standard render analyzer failed on missing task evidence; the presentation
stream parser rejected a byte-count mismatch. These failures are preserved and
must not be relabelled as complete render evidence. The allocator analyzer
found no recovered service/request snapshots, not zero actual allocations.
The hardware analyzer has samples through 122.289 seconds and no observed
sample loss or malformed records, but recovered no normal target-exit or
observer-stop record. A normal bounded target shutdown is therefore unproven.

The independent complete-image exporter did succeed with status 0. The exact
published ready marker is at monotonic 120005562 microseconds, FB 95. Both
12,288,017-byte PPM files validate structurally, and all 4,096,000 source/output
pixels match after the known clockwise rotation. 4,095,826 pixels are nonblack,
unlike 073's 4,652-pixel region. Source PPM SHA256:
`bd9ee73f2f5e0f6b504a3dae7e17bb68f310273cbb2395049f81723e5f431ec0`.
Output PPM SHA256:
`93f7a454dd226551b6d009b6afa941a209c5fb7888252f955759d3e3f3817003`.

`desktop-pixel-review/result.json` independently checks the exporter marker,
complete PPM schema, exact file hashes, dimensions and rotation without accepting
the malformed mixed trace stream. Local Windows OCR of the source PNG reads
the OOBE privacy page title and Continue button. This is OCR, not direct model
visual inspection: the available image viewer rejected image input. The user
also directly reported OOBE, then failure at the offline activation step.
These observations establish OOBE progress, not desktop or activation success.

The authenticated hilog ends at guest 48.274 seconds and does not cover the
whole UI session. `video-outcome-analysis.json` compares error-line counts, but
its zero candidate error counts cannot establish successful native decoding,
GPU YUV import or error absence later in the boot. Software readiness is not
decoded-frame evidence. Keep its explicit false verification fields.

Next experiment 075 follows the user's supplied HarmonyMac development path:
original Ability Manager starts SceneBoard and force-stops the original guide,
without claiming or forging activation. No 074 evidence or image is overwritten.
