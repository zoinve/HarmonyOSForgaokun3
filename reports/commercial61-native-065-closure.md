# Native 065: Original Root Layout Restored

## Outcome

The authentic desktop is not yet verified. Restoring the original root symlink
/chipset -> /vendor lets genuine HDF manager and composer publish their ready
events successfully at 10.223 and 10.929 guest seconds. The original init then
reaches boot.completed; public CLI rounds 2 through 4 read true. Original
BootAnimation observes completion and releases its RS node at 75.381 seconds.
No completion flag, ACL, credential, service binary or watchdog was changed.
The custom bootstrap is intentionally changed, not byte-identical to 064.
Only init and native-target/bootstrap differ in the initrd versus 064.

Original account 100 activation again succeeds, callback error 0 at 48.151
seconds and account.ready at 48.165 seconds. Early sparse images are black;
samples 20, 24 and 28 contain only 45 blue pixels (10,89,247), bounding box
x=11..17, y=125..131, against 40915 black pixels. No full-resolution visual or
interaction verification was performed. This is not desktop success.

## Freeze Evidence

Original SceneBoard PID 4010 freezes and the original watchdog/AMS kills it
for THREAD_BLOCK_6S at 84.277 seconds. PID 8875 restarts normally; first observed
SceneBoard flush is 100.222 seconds. Last sampled composer frame is 93.623518
seconds. Sampling limits prevent interpreting this as proof of no later commit.

Offline recovery found the complete original 614997-byte SceneBoard freeze
report in seven previously preserved fault snapshots (samples 9 through 15).
Every copy has SHA256
fcf48c98f3c7c492c31db0b6bb3b8f06bcbcd082eb371dd5b24f431fe858c056.
The existing strict extractor checked contiguous offsets, declared byte counts,
complete=1, changed=0 and read_errno=0. See freeze-extraction.json and
original-freeze-files. No additional operational boot was needed.

The main-thread native stack waits synchronously in BundleMgrProxy, called by
GetLauncherAbilityInfoSync, LauncherAbilityManager.getAppInfoByBundleName and
ResidentLayoutCacheMgr.createDockAppInfo/init. The original handler reports
uv_io_cb running since 52.982 seconds. Matching hilog at 52.982 seconds shows
foundation PID 1024 TID 3580 cannot find com.huawei.hmsapp.appgallery. At the
80-second process snapshot the main thread is in binder_thread_read/ioctl.
This identifies a blocked bundle-query path, not its server-side root cause.

After restart the same appgallery query lasts from 86.999 to 95.391 seconds
and fails with 8521220; settings query lasts 95.506 to 99.510 seconds and fails
similarly. Settings absence also prevents original startupguide Wi-Fi/local-user
extension discovery. Investigate original bundle availability and BMS wait path;
do not fabricate bundle entries, skip OOBE or disable the watchdog.

## Preservation

Run: commercial61-native-065-f83c6916-1f40-4d55-8088-a4da2ebcc091.
Single boot: 2026-11-14 18:49:54.443428Z to 18:53:36.102112Z.
Returned Ubuntu boot: 71f4df2d-6546-4d77-bfed-604a9032dc41.
All 64 retrieved files hash-matched; no journal replay. Full post-return checks
passed: Ubuntu current/default, original manual entry, firmware, four original
images, unmounted lab partition and enabled/active screen-off timer. Entry 063
was archived before authorized removal; latest entries are 064 and 065.
127 prior EFI files remain unchanged except normal loader/random-seed and the
explicitly authorized archived entry removal.

Hardware observation: 212 attachments; zero failures, lost/malformed records or
IP mismatches. 6088 log lines were suppressed, separately from perf loss.
Root-layout, event/account, executable-mapping, perf and workflow tests passed.
Authoritative hardware test metadata is hwbreak-test-revision3.json; revision2
is preserved historical output. Goal remains active. Do not rerun 065.
