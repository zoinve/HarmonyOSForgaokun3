# Task Manager CPU frequency dependency repair

Date: 2026-11-17. User identified HarmonyOS Task Manager as the affected UI.

## Observed Cause

Native458 phase-204.log records the same deferred probe before services and
later in the session: `18591000.cpufreq qcom-cpufreq-hw: Failed to find icc paths`
(lines 1414, 75116, 167227). Original hiview fails to read per-CPU
`scaling_cur_freq`, minimum and maximum frequency nodes, including during the
manual session at 10:15:01. Thus this is not only a missing UI formatter or a
root-only `cpuinfo_cur_freq` permission issue.

The matching local kernel source qcom-cpufreq-hw.c:663 calls
`dev_pm_opp_of_find_icc_paths` before registering cpufreq. The SC8280XP device
tree supplies an EPSS L3 interconnect provider. Ubuntu loads `icc_osm_l3`;
the native startup source does not explicitly load it. Ubuntu's CPU policies
are available (host observation470), but this does not prove native acceptance.

## Change And Verification

Candidate471 retains458 drivers and bounded manual window. It packages the
existing EPSS L3 provider built for `7.1.0-rc3-gaokun3-el2`, not the different
Ubuntu module. Its module metadata reports no module dependencies and the
`qcom,epss-l3` alias. Startup explicitly loads it before board modules and
performs a bounded read-only policy snapshot. No frequency, governor,
permission, authentication, original image or active data165 changes.

Test472: two tests passed. Candidate471 cross-compilation and overlay build
succeeded. Neither installed nor booted; retained173/458 entries unchanged.
Loading the provider is the evidence-backed repair candidate, not yet a
verified fix. Native policy registration and actual Task Manager display
still require a new guarded target run. Full driver goal remains incomplete.
