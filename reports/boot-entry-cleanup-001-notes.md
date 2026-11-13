# Consumed diagnostic entry cleanup001

Following explicit user authorization, four exact configs were archived and removed from `/boot/efi/loader/entries`: `harmony-native-diag-004+0-1.conf` through007. Each was checked byte-for-byte against its installation record and confirmed consumed. All116 collected logs were verified before cleanup.

Archives exist both locally in `reports/boot-entry-cleanup-001-backup/` and remotely in `/var/lib/harmony-lab-boot-entry-cleanup-001/`, with SHA-256 values in `boot-entry-cleanup-001.json`. Restoring a particular config can restore its entry, but its consumed counter must not be changed automatically or confused with authorization for another boot.

All70 other EFI files were verified unchanged during cleanup. The persistent Ubuntu default and firmware boot entries were checked unchanged; no one-shot was selected and no reboot was requested. Kernel/DTB/initrd assets, raw logs, original SDK images and unrelated Ubuntu test/recovery/fastboot entries were not deleted. Their continued usefulness has not been established, so a title containing TEST alone was not used as deletion authority.

`bootctl list` can still show the removed names as `Reported by Boot Loader (reported/absent)` from the current boot's `LoaderEntries` EFI-variable cache. The config files are gone; the cache was not manually edited and no extra reboot was performed merely to refresh it. A subsequent normal boot will rescan on-disk entries.

Future installer/preflight work must start from a fresh post-cleanup baseline rather than rerun old immutable scripts that expect these files to exist.
