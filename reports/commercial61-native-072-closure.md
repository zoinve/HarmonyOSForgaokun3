# Native 072 Closure: Software Backend Opens, Video Surface Allocation Fails

## Outcome

The real desktop objective remains active and unachieved. Native 072 ran once:
`commercial61-native-072-5c53bf37-0709-407e-abf3-86068c16f58f`.
Boot observation was 2026-11-14 21:50:24.858418 UTC through
21:54:06.524817 UTC. Ubuntu returned as boot ID
`1da831cc-f699-4549-9278-d0d20752ff50`.

The original AVC-open and HEVC-create failure messages observed in 071 no
longer occur. The original services instead fail later, allocating video
output Surface buffers: `allocator_host` returns -2, followed by
`Start codec failed: cannot allocate buffers` in FCodec/HevcDecoderLoader.
Consumer usage combines to 0x1035 in the relevant original-service messages.
This is original runtime progress, not proof of a decoded HarmonyOS video frame.

The captured full-resolution source and scanout bytes remain identical to
068-071: 4,096,000 pixels, 4,091,348 black, 4,652 nonblack. Source bounds are
[1242,1421,1317,1496]. Clockwise rotation matches with zero pixel differences.
Source PPM SHA256:
`7ec03e269b0b326237d07deffeb89c656691e4b696bf362075566c4f83f1b0a4`.
Scanout PPM SHA256:
`11cfdd1750f4b2267c99bdc56f306f877cf7c1637e30073e4967579fcf2af0f3`.
No semantic identification of the small nonblack region is established.
No visual inspection or normal desktop interaction is claimed.

## Implemented And Tested

See `commercial-software-codec-design-072.md` for protocol, reference roles,
private package extraction, runtime provenance and guarded XZ staging recovery.
Normal and ASan/UBSan native socket tests passed all eight exact original videos:
1980 frame hashes and presentation timestamps match. Isolated private-runtime
tests independently repeat those results. Malformed requests, exact UID and
full-slot ownership/backpressure were checked. No original adapter was replaced.

The archive admission verifies only init/bootstrap changed among existing 070
members; new members are the private runtime and two launchers. Original 070
resources, init-managed service definitions, identities, authentication and
read-only system-overlay behavior are preserved. Original-image writes and
installed-record changes were not introduced.

## Runtime Evidence And Limits

All 67 retrieved files matched their remote hashes. Presentation stream is
complete: first flush 104.91 seconds, 49 later sampled frames through 154.131612
seconds. The retained graphics execute-only observer made 212 attachments:
zero failures, lost samples, malformed records or instruction-pointer mismatches.
The target timeout and observer stop were normal. No 071 codec probes were carried.

Original app rawfile and source-setting errors remain zero. SystemResources
AddResource failure remains one. Generic video-decode-error log lines increased
from 9 to 18; these are log-line counts, not independent player/failure counts.

Helper-log observations used StartupGuide's process root and returned ENOENT.
Do not infer that the global helper logs are absent or that helpers failed.
No helper exit/restart lines like 071 were captured, but helper readiness and
real decoded frames inside HarmonyOS were not directly verified.

## Preservation

Post-return verification passed: Ubuntu current/default entry, firmware, original
manual entry, enabled/active screen-off timer and all four original image hashes.
The lab partition is unmounted. The only boot-managed change is the random seed.
User-authorized retention archived/hashed entry 070 before removing only that
entry; current experimental entries are 071/072. Shared payloads remain intact.
Retention record: `boot-entry-retention-20261114T215014388896Z/result.json`.

## Next Investigation

Do not rerun 072. Next unique candidate should preserve this real backend and
capture original allocator_host / av_codec_service maps and status, and the
actual public allocator request fields (format, dimensions, usage, expectedSize).
Read helper logs through a validated original service root, not the app sandbox.

The reference HarmonyMac allocator copied in commercial-allocator-015 supports
only four RGB formats; its interface defines NOT_SUPPORT as -2. Video-format
rejection is therefore a concrete hypothesis, but 072 does not establish the
effective allocator_host library or the failed request's exact format. Verify
those before extending format support. Any YUV allocation must include truthful
plane geometry, mapper validation and GPU import support, not just return zero.
