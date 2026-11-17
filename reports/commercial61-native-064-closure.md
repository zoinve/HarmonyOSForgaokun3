# Native 064: Public Boot Events And ACL Evidence

## Outcome

The genuine desktop remains unverified; all seven sparse 160x256 samples are
black. The single operational boot is complete and must not be repeated.
The 063 original account lifecycle repair again worked: original accountmgr
PID 3977 received OnStartUserDone(account 100, error 0) at guest 45.491 seconds
and wrote account.ready at 45.516 seconds. No boot flags or ACLs were changed.

Five complete public-CLI parameter snapshots and the diagnostic end marker were
retrieved. The final snapshot has true values for every scanned declared service
event except hdf_devmgr.ready and composer_host.ready, which both report error
106 (not found). Whole-system boot.completed also reports not found, while
persist.init.bootevent.enable reads true. This is actual CLI output, not an
inference from missing setter logs. CLI exit 0 is not parameter lookup success.

Original vendor ACL files are visible, readable and retain their original
service-specific 0775 rules. Public id queries resolve composer_host to 3036 and
hdf_devmgr to 3044; these are account lookups, not changed caller identities.
The original param ls reports both ready names not found. Other service ACL
queries return their original owners and SELinux types. The observations support
investigating missing vendor-rule loading; they do not directly dump all rules.

SceneBoard first flush was at 99.595 seconds, with two post-flush composer
frames ending at 120.062325 seconds. BootAnimationNode still drew at 120.020
seconds. Hardware observations: 188 successful attachments, zero failures,
lost records, malformed records or IP mismatches; 2071 sample log lines were
suppressed, distinct from perf loss.

## Preservation And Tests

Run: commercial61-native-064-eb75a279-368d-4801-a3a0-a3ad7928b1d9.
Single boot: 2026-11-14 18:33:51Z to 18:37:33Z.
Returned Ubuntu boot: 551f3788-f07f-4578-8011-cd59a9d63945.
All 64 evidence files matched remote hashes, with no partition journal replay.
Full return verification passed: Ubuntu current/default, original manual entry,
four original images, firmware, unmounted lab partition and enabled/active
screen-off timer. Entry 062 was archived before user-authorized removal;
063/064 remain, with shared payloads unchanged.

Offline tests covered the retained account flow, all scanned declared keys,
five bounded diagnostic rounds, command failure retention, mixed CRLF/LF byte
accounting, corrupted/truncated snapshots, exact initrd delta, synthetic perf
records, executable mapping integrity and workflow guards. Relative to 063 only
init and desktop-order020.sh changed. Original bootstrap and all service/library
and module payloads remained byte-identical.

## Original Layout Discovery

Read-only original init disassembly shows GetCfgDirList at VA 0x70d44 reads
const.cust.config_dir_layer (literal VA 0xc082), falling back to the literal
/system:/chipset:/sys_prod:/chip_prod at VA 0x10397. Normal parameter loading
uses GetCfgFiles("etc/param") at 0x34bec-0x34c20. The normal path does not use
the updater-only explicit /vendor/etc/param call at 0x34c54.

The original system image's root /chipset is a symlink to /vendor (inode 13,
seven-byte target). The custom bootstrap creates several root layout aliases
but omits /chipset. Thus the default configuration search has no valid path to
the otherwise readable vendor parameter directory. This is a concrete candidate
cause, not proof that no other startup gate remains. Candidate 065 should restore
only that exact original link in the volatile root, retaining original rules,
credentials, binaries and event writes by the genuine services.

Primary evidence: event-analysis.json, event-state064.log, account-analysis.json,
runtime-evidence and verifier outputs under commercial61-native-064. Original
vendor declarations/ACLs are in commercial-event-declarations-063-r2, correcting
the preserved first audit's wrong vendor filesystem-root assumption.
