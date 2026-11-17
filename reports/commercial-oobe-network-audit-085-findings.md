# Original OOBE Network Control Flow

Read-only decoding of the original guide HAP's InternetManager:19 methods,
711 instructions, all branch targets validated against instruction boundaries.
Original HAP/ABC and pinned ISA hashes verified by the audit script. Full evidence
is in `commercial-oobe-network-audit-085/decoded-methods.json` and `.txt`.

- `func_main_0` initializes NET_CAPABILITY_VALIDATED=16,
  NET_CAPABILITY_CHECKING_CONNECTIVITY=31 and DELAY_TIMEOUT=8*1000.
- `hasDefaultNet` calls the original connection API asynchronously. The callback
  subsequently calls `setConnectedChange` using the returned connection boolean.
- A change from disconnected to connected clears isValidated, emits
  WAIT_NET_VALIDATED and starts timeOutUtil. `isNetConnected` requires both
  isConnected and isValidated, not merely hasDefaultNet.
- `register` calls createNetConnection/register and subscribes to netAvailable,
  netUnavailable, netLost and netCapabilitiesChange. Its registration callback
  only logs success/error; that log does not mean network validation succeeded.
- `handleNetCapabilitiesChange` reads netCap.networkCap. If31 is present it
  returns without completion. Otherwise it clears the timer, assigns isValidated
  from includes(16), and calls netChangeEvent.
- Timeout callback logs the exact eight-second warning seen in084, assigns
  isValidated=false and calls netChangeEvent.

084 first guide6213 received netAvailable and capabilities12,15,16. Later guide
instances9121/11968 saw hasDefaultNet:true but no recorded capability callback
before the eight-second timeout. This supports investigating callback delivery
and restart timing. It does not alone prove a particular NetManager defect or
that the first guide completed activation. No guide method or binary was patched.
