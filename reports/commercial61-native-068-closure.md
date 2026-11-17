# Native 068: Complete Original Client Target And Scanout

## Result

Genuine desktop and interaction are not achieved. This completed single boot
provides actual full-resolution evidence that changes the next investigation:
the missing content is already absent from the completed client target.
Do not repeat operational 068.

Run: commercial61-native-068-87626cde-3bf6-44d5-9329-7bce85fcd784.
Boot observation: 2026-11-14 20:06:34.137128Z to 20:10:16.186185Z.
Ubuntu return boot: f727dede-5258-496e-a258-a650e4c28b4d.

## Full-Resolution Evidence

The read-only capture runs after completed page-flip, under the existing
composer mutex, with source/output DMA read synchronization. It maps the
actual client target PROT_READ, reads the actual scanout mapping, converts
the declared RGB/BGR channel order and omits stride padding. Neither original
mapping is written. A ready marker is published only after both files and DMA
sync completion succeed. The outer worker verifies owner, type, sizes, EOF and
stable metadata, copies under an eight-second deadline, then publishes the
run's ready marker. Failed/partial files cannot pass the image analyzer.

Capture: 120.020494 guest seconds, FB 96, 300550 microseconds duration.
Both PPM files are exactly 12288017 bytes. Export status is zero.
67 retrieved files match their remote hashes; no partition journal replay.

| Map | Dimensions | Nonblack Pixels | Nonblack Bounding Box |
|---|---|---|---|
| Client source | 2560x1600 | 4652 / 4096000 | 1242,1421 through 1317,1496 |
| Scanout output | 1600x2560 | 4652 / 4096000 | 103,1242 through 178,1317 |

Exactly 4091348 pixels are black in each map; 4316 are RGB 10,89,247.
Rotating the complete source clockwise yields zero different output pixels.
This is pixel-exact proof for this completed frame, not a general claim about
every frame, physical panel visibility or interactions. It excludes loss in
the source-to-scanout rotation/copy for this frame. It does not prove that
every original UI draw or resource read succeeds upstream.

Source PPM SHA256: 7ec03e269b0b326237d07deffeb89c656691e4b696bf362075566c4f83f1b0a4.
Output PPM SHA256: 11cfdd1750f4b2267c99bdc56f306f877cf7c1637e30073e4967579fcf2af0f3.
Original PPMs remain in runtime-evidence/raw. Lossless derived views are
full-frame/source.png and full-frame/output.png, with hashes and exact pixel
statistics in full-frame-analysis.json. The image-view tool refused image
input for this model; no visual inspection or object identity is claimed.

## Retained Original Lifecycle

SceneBoard first flush is 102.950 seconds. Complete presentation trace is
52191 bytes, sample 30, EOF verified, through 154.832970 seconds. SHA256
02f8484f52908189cda8aedac0dfdba5d6f8a93f6923578fef7b4306807ce668.
51 subsequent composer frame records have nonblack source/output samples.
204 hardware observation attachments, zero failures/lost/malformed/IP mismatch;
4768 sample log lines suppressed. The target ends under its normal bounded
diagnostic timeout and the observer stops. None establishes a usable desktop.

## Tests And Preservation

Exact helper tests compiled with address/undefined sanitizers pass: byte-exact
RGBA/BGRA/stride conversion, unchanged source arrays, malformed dimensions,
no-overwrite publication, partial markers, ownership, symlinks and export caps.
P6 schema, truncation rejection, full pixel statistics and lossless PNG CRC/
round-trip tests pass. Exact composer source reversal recovers 030 source.

Archive comparison permits only init, bootstrap and the custom composer to
differ from 067. Bootstrap adds the private diagnostic directory owned by the
existing composer UID 3036; service credentials do not change. Outer init adds
bounded file export and the experiment name. All original service binaries,
EGL, account restart, root aliases, parameters and other members are identical.

Installed overlay SHA256:
8d0f35e29bb9ba9a5c1b613e4dd58b93e142d91393e71bf8aa7d1fce84463d6e.
Post-return verification passes: Ubuntu current/default, firmware, original
manual entry, four original images, unmounted lab partition, screen-off timer
enabled/active. 130 prior EFI files unchanged; exceptions are normal random
seed and archived/hash-matched authorized removal of experimental entry 066.
Only experimental entries 067/068 remain; shared payloads were retained.

## Resource Boundary And Next Work

Read-only UI input audit confirms welcome_land_one.mp4 and welcome_land_two.mp4
exist, ZIP_STORED, CRC-valid in the original StartupGuide HAP. SystemResources
also exists and passes ZIP CRC, despite original runtime AddResource failure.
See commercial-ui-resources-audit-068.md; ZIP CRC is not signature or semantic
resource-manager validation.

Original 068 logs explicitly report FindRawFile path to realpath error
immediately before both welcome video resolution failures. Offline 069
disassembly confirms the original FindRawFile filesystem lookup, without
executing, patching or reading live private objects. Next verify the actual
stock resource index directory and application sandbox paths. Do not replace
private functions, force-stop StartupGuide, forge installed records or write
provisioning flags to hide the original workflow.
