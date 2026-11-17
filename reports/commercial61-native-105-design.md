# Native server capture-order correction 105

104 proved original DFX capture works, but its snapshot was 1275 ms after the
first client query returned. Do not replay 104 or use that stack as wait proof.

105 invokes the unchanged original probe before the per-thread proc survey,
retaining the five-second first-guide trigger. Explicit DFX call markers and
uptime bound the call. Proc samples are labelled post-capture only. Require new
timestamp evidence of actual query overlap; a successful API result alone fails
the wait-cause evidence gate. No causal latency comparison is claimed.

The sole observation-order change does not alter original service startup,
identity, network, authentication, sandbox checks, OOBE callbacks or watchdogs.
The reference aa action remains single-shot. Runtime bootstrap and native probe
remain byte-identical. The RAM outer exporter renames its dedicated log and
external bootstrap path; its hash change is tracked by the early wrapper.

Admit exact archive/source changes, observer failure and ordering tests, ordered
overlays and isolation/preservation guards before a single bounded boot. Archive
entry 101 before authorized removal; retain 104/105, Ubuntu default and original
manual entry. Serial read-only noload retrieval, privacy and preservation checks
remain mandatory. Desktop success still requires stable visible native desktop
and correlated interaction; a stack probe is not a substitute.
