# Headless diagnostics 875

- Experiment 874 completed with all original disk and protected userdata hashes unchanged.
- 875 read-only snapshots show SceneBoard and OOBE main threads waiting in epoll; this is not proof of a deadlock or full responsiveness.
- Screenshot `next-experiment/ui-diagnostic-875.png` is still the black OOBE frame with the blue next arrow, not a desktop.
- The 875 hilog invocations failed: `-x` and `-z` are mutually exclusive query modes. Exit status was misleadingly zero. Prepared fresh 876 payload with `-z` alone and ordinary-shell ability dumps; it makes no activation or account changes.
- Read-only extraction of completed 874 userdata log files found SceneBoard's `BaseOobeManager: sessionExceptionCallback is called`, followed by `start oobe again` and `start oobe ability`. This directly explains the observed OOBE respawn after the single authorized termination.
- Logs also explicitly suppress the dock with `isOobeActivated: true`. No readiness or activation state has been changed to hide this condition.
- Persisted desktop logs contain dictionary/binary encoding. NUL-separated readable application messages were inspected only; undecoded native messages are not treated as understood.
- Host physical backlight remains at actual brightness 0. No viewer has been opened.

875 post-run hash results remain subject to runner completion; desktop is not verified.
