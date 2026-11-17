# Native 076: init rejected the diagnostic service

- Exactly one boot: commercial61-native-076-025643df-7eef-469a-aba3-19c2c82193dc.
- User reports OOBE still visible. No guide dismissal or desktop success claimed.
- interactive-faults030.log records init_service_manager.c:1028:
  `Failed to get path for service matebook_desktop076`, followed by line 1218:
  `Service error matebook_desktop076 parse config error.`
- interactive-hilog030.log:26201 registers the diagnostic native token with
  `permSize 0`. This is not evidence that the requested permissions were granted.
- The command snapshot and second capture are absent from the 63-file retrieval.
  Do not infer CLI execution, a successful stop, or a guide restart.
- All 63 remote file hashes matched. Returned Ubuntu boot ID:
  97b33c81-ca90-412f-bd98-bd2f7ad692f0.
- Independent pixel review validates a complete 2560x1600 source capture at
  120013763 us and its 1600x2560 output with zero rotation differences. Local
  OCR reads the language-selection OOBE, not a desktop. Source PPM SHA256:
  408cae3ae1d4554bfec6a279fb32082fe200340351a2fd5ed50e621bc6ddbf4b.
- Hilog ends at 52.440 seconds. Second capture, keyboard, command snapshot and
  target exit evidence are absent. Missing records do not prove no later events
  occurred, nor do zero recovered codec failures establish successful decoding.
- Return verification preserved Ubuntu current/default, original images,
  firmware, manual entry, enabled/active screen-off timer, and unmounted LAB.
- Next candidate 077 moves the inline shell program out of init argv into a
  separate script. Runtime startup, permissions, guide dismissal, desktop pixels
  and interaction remain unverified pending its own bounded experiment.
