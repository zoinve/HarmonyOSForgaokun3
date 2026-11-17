# Duplex Candidate Local Verification

Date: 2026-11-17, Asia/Shanghai. Basic-driver goal remains incomplete.
Priority remains Bluetooth, physical multitouch, audio, then actual 120Hz.

Continued the unverified410-414 implementation without changing target401,
desktop173, protected data165/197, boot configuration or original services.

415 initially exposed a generator bug: the c_* function enumeration matched
calls inside unrelated function bodies. Restricting the match to the function
declarator prevents accidental removal of a_destroy_capture. After that fix,
the generated server compiled for ARM64 with -Wall -Wextra -Werror, and the
generated shared VDI compiled with the pinned official headers and
--no-undefined. Temporary generated sources and binaries were automatically
removed. Repro: next-experiment/test-audio-build-415.py under WSL Debian.

416 passed GCC AddressSanitizer and UndefinedBehaviorSanitizer. Its UCM fixture
checks exact microphone PCM selection, one stream per direction, shared manager
ownership, capture close preserving playback, enable failure preserving the
other lease, rollback fault quarantine, final-release reset, and invalid release.
No real microphone was opened or sampled. This fixture does not validate ALSA
hardware behavior, worker concurrency, transport, VDI capture or physical sound.

Remaining before deployment: capture protocol/partial-read/VDI mute and position
fixtures, bounded worker shutdown, review of error handling and shared-card
failure recovery. No new target boot or installation occurred.401 remains the
last verified target experiment; do not repeat it. Bluetooth pairing/reconnect,
physical multitouch, acoustic output and120Hz acceptance remain pending.
