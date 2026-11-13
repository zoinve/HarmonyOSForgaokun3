# Experiment 881: blur-disabled, 960×540 diagnostic

Native ARM/KVM, independent userdata, physical screen off. The RAM boot configuration adds only `setparam persist.sys.graphic.blurEnabled 0` after loading persistent parameters. The runtime value has not been independently queried.

Actual screenshots show normal navigation through language, region, quick setup, software agreement, and data privacy. The normal agreement was accepted with the user's explicit authorization. No activation, account, trust, or readiness state was manually changed.

`privacy-focus.png` shows keyboard focus on Continue. Enter transitions to the empty card in `after-privacy.png`, which persists in `privacy-settled.png` and `privacy-late.png`. This is not a desktop.

Read-only extraction from the live independent userdata (potential snapshot inconsistency) shows the application received the privacy Continue action and loaded `activation_lock` / `FindServiceOOBEActivationLock`. Its own log reports a 540-pixel screen, approximately 400 vp, and `contentMaxHeight is -60.00000706425408`. Therefore the diagnostic resolution produces an invalid content height; a blank page is not by itself evidence of a whole-system hang. Activation-code and MDM log messages have not been interpreted as successful activation.

RenderService warnings also still show CPU work inside Mesa softpipe's TGSI interpreter. Disabling blur is not established as a complete fix. In contrast to experiment 880, the quick-setup-to-agreement transition did complete, but causation is not proven.

Next bounded comparison: restore the original 1920×1080 output with the same payload and all other options unchanged. Verify the real page contents. Preserve original-image integrity checks and remove only stopped experiment userdata after results and evidence are saved, as requested.
