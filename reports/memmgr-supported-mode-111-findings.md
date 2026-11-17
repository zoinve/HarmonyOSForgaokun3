# Memory service supported-mode comparison 111

Offline inspection only; no boot, image, kernel, or service modification.

Primary source: references/openharmony-memmgr-111, OpenHarmony
resourceschedule_memmgr, HEAD ae0095521ed66344c08ebf8a588b9a254ede9704.
This source is not proof of equivalence with the supplied commercial binary.

## Verified source findings

- services/memmgrservice/BUILD.gn defines USE_HYPERHOLD_MEMORY when the
  build argument memmgr_hyperhold_memory is enabled.
- services/memmgrservice/src/mem_mgr_service.cpp conditionally compiles
  ReclaimStrategyManager initialization under USE_HYPERHOLD_MEMORY.
  This is a compile-time alternative, not an XML runtime switch.
- services/memmgrservice/src/reclaim_strategy_manager/reclaim_strategy_manager.cpp
  unconditionally calls SetRootMemcgPara inside ReclaimStrategyManager::Init
  after event handler creation and available-buffer initialization.
- services/memmgrservice/src/reclaim_strategy_manager/memcg.cpp writes
  memory.app_score and memory.zswapd_single_memcg_param, then compares
  readback score and three ratios. Filename presence alone is insufficient.

## Relation to original evidence

The original 109 logs and original-binary disassembly documented in 110
prove that reclaim-strategy initialization executes and fails before SA
publication. Runtime Hyperhold disabled due to storage size did not omit
this initialization. Do not present the open-source build switch as a
runtime fix for the supplied binary or substitute a rebuilt service.

Not every possible proprietary configuration escape has been excluded.
Original XML and emulator-specific branches remain to be inspected.
Next investigation: genuine kernel-interface semantics and actual
reference-runtime mounts, without diagnostic placeholder success.

Stable interactive original native desktop remains unverified.
