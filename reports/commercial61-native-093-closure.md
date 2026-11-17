# Commercial 093: unbooted candidate withdrawn

093 was built and installed but never booted. Preboot inspection found that the
original parameter CLI can emit leading whitespace and CR/LF, while the privacy
diagnostic expected exactly 64 hex characters without normalization. Therefore
the candidate could not reliably establish its original UDID privacy digest.

The entry and unique early overlay were archived and withdrawn, with hashes and
unchanged shared payloads recorded in
`commercial61-native-093/unbooted-withdrawal.json`.
094 corrected whitespace normalization and used the same genuine early hardware
input wrapper. No runtime outcome or native identity success belongs to 093.
