# Native 076: Init-Managed Diagnostic Caller

075 proved that starting the original `aa` binary before original init is not
equivalent to a normal developer shell: that process had no valid AccessToken.
Original AbilityManager rejected both the SceneBoard start and guide stop.
SELinux permissive did not and should not override these checks.

076 does not borrow a token or change an existing service identity. It adds
one separately named service, `matebook_desktop076`, to the existing RAM-only
init config overlay. Original init creates the process and issues its native
token from explicit permission declarations. The requested permissions are
START_ABILITIES_FROM_BACKGROUND, GET_BUNDLE_INFO_PRIVILEGED,
KILL_APP_PROCESSES, CLEAN_BACKGROUND_PROCESSES and DUMP. The diagnostic runs as
root with its own `sh` SELinux domain; every original service definition and
permission remains unchanged. The service is boot-started and once-only.
An actual runtime token and successful guide dismissal are not assumed from
configuration alone.

The service executes the same readiness-guarded reference commands as 075.
The unsuccessful pre-init script is replaced by a no-op, while the bootstrap
binary remains byte-identical. The actual diagnostic command log deliberately
retains the previous export filename `snapshot075-commercial-direct-desktop075.log`;
its content is now labelled COMMERCIAL076. Composer, allocator, EGL, codec,
resources, original images and the account-order wrapper are unchanged from 075.
Both complete real-buffer captures and the physical LEFTMETA event remain.

Only the outer init's numbered path/markers change; the incremental archive's
three changed members are `init`, `native-target/samgr_standard005.cfg`, and
`native-target/commercial-direct-desktop-075.sh`. All original service objects
are structurally compared before and after config modification. The exact
delta, original bootstrap, explicit permissions, absence of supplied token
values, eight-part ordered parent chain and workflow syntax pass admission.
Overlay size 356621 bytes; SHA256
`2183177b065d0a405af7a7507e2f8ee0e00035838c4c967b6b3fa88e24e00f2f`.

EFI space was restored without lowering the 32 MiB guard: cleanup 002 archived
the unreferenced `commercial61-native-047/initrd.img` outside EFI, verified its
SHA256 before deletion, and verified all 139 other files plus firmware/configs
unchanged. No current config references that directory; none of the shared
001/017/016/072/073/074/075 parent payloads was removed. Free space rose from
33669120 to 43884544 bytes. The original 047 evidence and archive remain.

Ubuntu current/default boot, screen-off timer enabled/active, unchanged source
images, old manual entry, one bounded boot and exclusive numbered evidence
remain required. Desktop/interaction/activation are all unverified at admission.
