# Experiment 876: genuine keyboard-driven UI progress

- Native ARM/KVM; independent userdata; physical display remained off.
- Completion checks: original read-only images and protected original userdata unchanged.
- Connecting a headless RFB client alone did not change the black welcome page.
- QMP Tab produced a visible focus ring around the welcome arrow. Enter activated it; after settling, a genuine Chinese language-selection page appeared (`next-experiment/welcome-settled-876.png`).
- A subsequent Enter started another transition. The bounded guest ended before its settled result could be inspected. This is not evidence that navigation failed.
- No agreement was accepted, identity changed, or completion state fabricated. No genuine desktop yet.

This disproves a complete UI/input freeze for that observation interval. Short waits during software-rendered transitions were insufficient to judge responsiveness. Experiment 877 uses a fresh userdata copy and a 1200-second headless window for screenshot-verified navigation.

Read-only shell diagnostics still produced no decoded output from the corrected hilog queries or ability dumps; exit status zero alone is not success evidence.
