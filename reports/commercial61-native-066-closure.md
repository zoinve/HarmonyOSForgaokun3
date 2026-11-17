# Native 066: Complete Bounded Presentation Evidence

## Result

Authentic desktop pixels and interaction remain unverified. This single boot
changes only the custom bootstrap's read-only trace capture: the former 32768
byte prefix reader is replaced by commercial_stream043 with a 262144 byte cap,
explicit byte counts, EOF and error status. All other initrd members except
init and native-target/bootstrap are byte-identical to 065. Original service
binaries, account script, parameter payloads and graphics libraries are unchanged.

The final complete trace is 52266 bytes, selected sample 30, SHA256
0cf4b2b0047e9d4cac82c0c0b98ce619ac7a94670caec072f5398af0a6a2398a.
Its EOF and actual stream byte count are verified. It contains 89 complete
composer frame records through 154.744747 guest seconds. SceneBoard's first
observed flush is 105.995 seconds; 49 subsequent frames have nonblack source
and output samples. Late source samples contain only 49 nonblack points and
output samples 45. Output sparse images at samples 24 and 28 are the same
tiny blue shape as 065, SHA256
2a2b5a79090b8731f422877e2daf85338476a52ed4b19f74500ac085b805350d.
Other captured samples are black. Sparse samples are not full-resolution proof.

This corrects the evidence gap in 065: its trace prefix ends mid-record at
93.623518 seconds. Missing sampled post-flush frames there cannot establish
that composer stopped. In 066, composition continues but the sampled client
target already lacks substantial scene content. Output rotation alone is not
an established explanation for absent desktop content.

## Original Lifecycle And Scene Evidence

Original HDF and composer events succeed at 9.617 and 10.292 seconds. Account
100 activation callback returns error 0 at 51.987 seconds; account.ready is
written at 52.083 seconds. Original BootAnimation reads boot.completed true
and releases its RS node at 74.779 seconds. All five event snapshot rounds
are complete; the original 065 chipset alias marker remains intentionally
unchanged in the retained bootstrap helper.

SceneBoard restarts under its original lifecycle/watchdog. The second process
8494 exposes wallpaper/desktop windows at 90.801 seconds. RS logs at 106.012
seconds show hwstartupguide0 in the occlusion list and desktop/wallpaper state
2; matching window visibility logs follow at 106.020 seconds. The welcome
page reports entry at 96.162 seconds and invalid video source/surface messages.
RS repeatedly draws VideoDecoderXComponentSurface from 110.013 through 155.001
seconds. These identify scene/workflow boundaries, not a complete root cause.
Do not force-stop startupguide or write provisioning flags.

An independent debugfs cat read of each audited original Settings, PCSettings,
Camera and AppGallery file matches the prior extracted file hash and size.
Thus the previously observed package structure/CRC problems are present in
the supplied source image, not explained by transient dump-file corruption.
See commercial-bundle-inputs-audit-066/independent-source-verification.json.

## Tests And Preservation

Stream tests reproduce truncation at 32768 bytes and recover all 40000 fixture
bytes at the new cap with EOF. Synthetic current-format hardware records,
executable identity tests, account/event regressions and workflow guards pass.
The first fixture compile and a stale older-format synthetic fixture failed;
their work directories/logs remain preserved. Revision3 is the successful
compiled fixture. Presentation parser tests reject wrong byte counts, missing
end markers, wrong paths and incomplete frame fields.

220 hardware attachments, zero failures, lost/malformed records or IP
mismatches; 4714 sample log lines suppressed, distinct from perf loss.

Run: commercial61-native-066-dc181d75-62ed-4c53-94bb-eaa139d3cb7d.
Single boot: 2026-11-14 19:17:51.023324Z to 19:21:33.018541Z.
Returned Ubuntu boot: b9b97dac-c087-49ca-b81c-e19f574a7195.
64 retrieved files hash-match; no partition journal replay. Full post-return
verification passes: Ubuntu current/default, original manual entry, firmware,
all four original images, unmounted lab partition and enabled/active screen-off
timer. 128 prior EFI files unchanged except normal random seed and archived,
user-authorized removal of entry 064. Latest retained entries: 065 and 066.
No numbered operational experiment is repeated. Goal remains active.
