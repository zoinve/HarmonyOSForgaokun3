# Commercial desktop 029 — observe actual presentation returns

028 proved native display acquisition, EGL initialization and context creation in the original SceneBoard process, but captured scanouts remained black. Entry-only tracing did not establish whether MakeCurrent, window-surface creation or buffer submission succeeded.

029 adds bounded return logging to those three own bridge functions. Their complete original bodies are unchanged; each wrapper calls its implementation once and returns the exact result. The logger preserves errno and does not consume EGL errors. The valid original HiLog domain and eight-message per-stage quota remain, with 22 known stages and at most 176 messages per process. No application permissions, identities, sandbox, authentication, frontend libraries or service binaries change. The three-reference adaptation baseline and original commercial runtime remain; no SDK userland is substituted.

The compiled native fixture verifies both zero and nonzero results, single invocation and errno preservation. Twelve scoped offline regressions passed; historical operational tests were not rerun. Public provider exports match the prior bridge, the bootstrap is byte-identical, and ordered archive extraction matches the full build including modes and parent ordering.

The final overlay is 736,649 bytes, SHA256 `f920c16788f020678166d9c7fbb0c85f17c1ee121cb9e5b67adc62a9ba98f7ed`. The chain remains commercial 001 → 017 directories → 016 hardware → 029 final. Trusted per-command SSH, standard Ubuntu current/default guards, enabled/active screen-off timer, original image hashes, manual entry and 32 MiB EFI reserve remain required. The 8 GiB volatile data, memory admission, 90-second target budget, 210-second outer deadline and bounded cleanup remain; software deadlines do not guarantee recovery from a kernel hang.

Runtime results are pending. A process, an EGL success or a submitted buffer is not proof of a genuine desktop; actual original desktop integration and captured display content remain required.

Installation succeeded: both non-PID1 guards refused with exit 77; all 122 prior EFI files were unchanged. EFI free space is 221,917,184 bytes. Ubuntu default, manual entry and enabled timer were retained. Installation itself selected no one-shot entry and requested no reboot. A separate single bounded 029 attempt has now been launched; guest results remain pending.

## Actual result (closed)

The single attempt ran from 17:21:25 to 17:24:17 UTC on 2026-11-13 (local November 14). All 59 exported files matched their hashes; retrieval mounted the original evidence partition read-only with `noload` and subsequently unmounted it. Configured target termination is recorded. No operational attempt was repeated.

Original SceneBoard PID 3514 initializes EGL, creates a non-null context and returns true from MakeCurrent. Original RenderService PID 917 also returns true from MakeCurrent, creates non-null window surfaces and returns true from SwapBuffers. These are genuine function-return observations, not inferred from entry logs. They do not prove meaningful scene composition or visible desktop content. All three actual 160×256 scanout captures remain entirely black. **The commercial desktop is not obtained.** Investigation therefore moves to scene/content and composition evidence rather than assuming EGL initialization is blocked.

Post-return verification confirms standard Ubuntu boot ID `b1df4c58-3262-4cdc-ad44-719853c64c4b`, unchanged current/default entry, firmware and original manual entry, no one-shot entry, unmounted LAB partition, and enabled/active screen-off timer. All four original commercial image hashes remain exact. Of 122 pre-existing EFI files, 121 remain unchanged; only the legitimate boot-managed random seed rotated. Historical raw logs and JSON evidence are unchanged.
