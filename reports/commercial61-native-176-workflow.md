# Native176 workflow readiness, not deployment

Date: 2026-11-16. This supplements the earlier build-only report.

## Implemented

`commercial-workflow-176.py` preserves the inherited authenticated bounded boot,
original image and EFI hashes, Ubuntu default, firmware checks, screen-off timer,
ESP capacity guard and one-attempt rule. It additionally:

- Requires the genuine USB subsystem ancestor, VID/PID346d:5678, removable1,
  exact61849600 sectors, exactly one matching disk and no additional USB disks.
- Refuses mounted media, including mounted child partitions. It never unmounts,
  opens raw media, changes USB role or requests write-enable.
- Runs this preflight before installation-directory creation and again before
  the one-shot/reboot commands.
- Places the final overlay at `/boot/efi/usb176.img`, with its hash checked
  against the admitted overlay. Local full-chain identity remains unchanged.
- Checks the existing1800 command-line bound before installation writes.
- Excludes the completed175 early-return run by its verified run ID from
  subsequent normal evidence retrieval, without weakening the manifest rules.

## Evidence And Revision

`commercial61-native-176/workflow-admission-r1/workflow-test.json` records six
fixture tests and compilation of all generated operations/remote payloads.
The initial generated scripts and workflow-test at the report root are retained
but superseded: review found they did not exclude175's completed run. They were
never executed against the target. The wrapper now requires the r1 scripts and
checks generated-source equality before execution.

`check-usb-readiness-176.py` performs only read-only target queries. Its successful
timestamped result under `commercial61-native-176/readiness-*` reports:

- USB readiness false; no installation or reboot attempted.
- Actual original-manual options plus the short chain estimate1785 bytes, <1800.
- Working173 entry present; candidate176 entry and alias absent.
- Target modified false; reboot requested false.

An earlier unprivileged readiness collection failed before emitting a result;
no installation/reboot code was involved. The successful invocation uses the
existing per-command sudo transport to read the root-restricted ESP. No global
permissions, SSH or sudo configuration changed.

## USB Disappearance Evidence

`usb-events-178-20261116T095425309000Z/result.json` contains fixed-field sanitized
events from the current Ubuntu kernel buffer. The preceding journal-only report
is retained separately. All three journal queries returned1 with no matched
events; this is not evidence of no USB faults. The dmesg collection succeeded.

Current boot5893962b-5856-42d2-8d21-3f399d415419 contains a connection on route3-1
at1.029544 seconds and a disconnect at43.176260 seconds. No identity event ties
this route to346d:5678 in the captured fixed-field records. No descriptor/address
error event matched. Therefore neither U-disk identity, physical unplugging nor
electrical/protocol failure is established by this record alone.

Five collector tests passed, including serial-line exclusion, trailing-private
text removal, numeric error parsing, connection speeds and remote syntax. Raw
kernel messages and USB serials were not exported. No new native boot occurred.
Actual HarmonyOS removable-node exposure, filesystem access and native-service
acceptance remain outstanding; the working173 desktop runtime is preserved.
