# Experiment 091: original identity APIs and conditional real hardware input

Retain 090 original services, SceneBoard canonical config, signed packages and
bounded real network refresh. Add one small platform-native helper to the
existing owned diagnostic service, without adding permissions or service IDs.

The helper requires original init as target PID 1, UID 0 and the original
SceneBoard HAP size. Read the original GetParameter and GetDevUdid APIs without
printing identity values. Require kernel sysfs DMI product/chassis serials to
be matching nonplaceholder 16-character alphanumeric values. Compare runtime
manufacturer/model to the actual DMI vendor/product, not to L410 fixture data.

Preserve any existing valid identity without writing. Refuse API errors,
nonempty invalid identity fields, inaccessible firmware, different product
metadata, or a conflicting boot serial. Only if metadata matches this physical
MateBook and no UDID exists may original SetParameter supply missing boot.sn
from firmware. Read it back and require exact firmware equality. Only then
load the byte/hash-verified original libudidmodule and query original GetDevUdid.
Do not calculate a substitute UDID, mutate manufacturer/model or provisioning,
impersonate another device, patch a signature or suppress a permission error.

This hypothesis can legitimately refuse all writes when the runtime image still
describes L410/default hardware. Such refusal supplies direct original-API
evidence for correcting the early hardware-parameter pipeline, not a successful
desktop or identity migration. Identity validity is not activation approval.

The existing diagnostic's timeout bounds the helper to eight seconds. Original
module and helper hashes are verified before invocation. Failure does not stop
normal original services or the existing bounded network observation. Retain
Ubuntu default, automatic return, screen-off timer, original images/manual
entry, shared payloads and numbered evidence. Keep experimental entries 090/091
after archiving 089. Retrieve first, then preservation verification serially.
