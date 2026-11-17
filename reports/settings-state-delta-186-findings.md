# Settings state-migration difference186

## New evidence

The supplied installer contains state-seed.tar.zst as well as the four original
filesystem images. Read-only scans183/184 inspected all 44,929 archive entries.
There are 27 regular HAP members; none has a Settings-related path. The original
BMS signature_files directory is present but has no archived children.

Audit185 queried the supplied BMS main and slave databases in memory. Both
contain installed_bundle and preinstalled_bundle records for
com.huawei.hmos.settings, versionCode600000412. Recorded paths include
/system/app/Settings/Settings.hap and
/data/app/el1/bundle/public/com.huawei.hmos.settings.
These are supplied preinstalled-state records, not proof of a valid signature,
matching code integrity, successful original installation, or a usable UI.
The two database hashes differ; neither is silently substituted for the other.

The first unmodified SQLite deserialize query failed with SQLITE_CANTOPEN.
The main archive WAL is zero bytes and no nonempty slave WAL is present in184.
For offline queries only,185 normalized bytes18/19 from0202 to0101 in a temporary
memory copy. Exported SHA256 values describe the original bytes. No database
files or target state were written; no WAL transactions were discarded.

## Relevant reference difference

HarmonyMac ed213a08817c642e9b455fb7d8f5271da41631eb:
ports/tools/populate-rootfs.sh stages the original .hmos-data subtree, excluding
the optional Debian compatibility root, and retains its label sidecar.

Our prepare-oobe-seed-123-remote.py explicitly copies only settingsdata.db and
settingsdata_slave.db onto a pristine seed. It does not copy the supplied BMS
databases. This is a meaningful difference to investigate, not proof that source
state restoration alone would work. It does not establish that HarmonyMac's
observed Settings success used byte-identical application or database inputs.

Historical native153 rejected Settings.hap for a missing HAP signing block and
error8519742. Native173 independently observed the absent user100 bundle and
launch error2097152. Neither observation is reclassified or overwritten here.

## Repair boundary

Investigate the complete supplied preinstall provisioning mechanism and the
coherence of BMS, access-token and application state before any candidate boot.
An existing database row must not be treated as a replacement for verification.
Do not manually insert records, transplant one row into the current BMS database,
disable verification, re-sign Settings, or replace it with PCSettings.

Any recovery experiment must use a separate candidate data filesystem and
preserve active persistent-data165 and desktop173. It must retain original
authentication and service checks, real device identity, Ubuntu default boot,
bounded return, and original image hashes. Launch acceptance requires the real
MainAbility, process/window evidence and actual usable Settings UI.

No target operation, boot or repair was performed in183-186. USB remains paused
at181. Focused tests183/184/185 passed 4+3+4 cases; these test analysis scope and
privacy guards, not application installation, trust or UI functionality.
