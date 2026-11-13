# 当前状态与源码入口

## 当前手动启动组合

`build-manual-gpu-041-cleanup-001.py` 生成只含 041 composer 的小型覆盖归档；底包使用原始 032 手动 initramfs，内核和 DTB 使用 031。其 `/init` 不变，没有 033 以后受控测试的 240 秒目标预算与 420 秒独立自动返回进程。菜单参数 `panic=0`，不存在“只改标题、实际仍有 watchdog”的情况。

`install-manual-gpu-041-cleanup-001.py` 为本机安装并归档旧鸿蒙菜单文件：不删除旧内核、镜像或证据，也不修改 Ubuntu 默认启动。此脚本依赖特定 ESP、哈希和本机基线，**不适合原样用于其他设备**。

当前组合没有再次启动；其 032 手动 init 与 041 GPU composer 已分别检查/实测。新组合仍需人工验收。后续用户明确要求关闭实验强制熄屏定时器，已持久禁用；旧报告中“保留每十秒强制熄屏/重启恢复”的记载是历史状态，不是当前要求。GNOME 正常空闲熄屏策略没有改动。

## 主要源码

| 方向 | 文件 |
| --- | --- |
| Binder PID 修复 | `next-experiment/native-binder-pid-031.py` |
| 独立内核构建/验证 | `build-native-binder-kernel-031.py`、`verify-native-binder-kernel-031.py` |
| 软件光标像素/状态/适配器 | `native-cursor-pixels-032.h`、`native-cursor-state-032.h`、`native-cursor-adapter-032.cpp` |
| CPU NEON 旋转与回退 | `native-rotation-034.h`、`native-cached-copy-034.h` |
| GPU 两遍渲染 | `native-gpu-composer-041.h` |
| 原始 composer 接入构建 | `build-native-render-041.py` |
| GBM/GPU 正确性测试 | `test-native-gpu-composer-041.cpp`、`test-native-gpu-formats-042.cpp` |
| 阶段统计/去重分析 | `analyze-native-render-034.py`、`analyze-native-render-041.py` |
| 当前手动覆盖包 | `build-manual-gpu-041-cleanup-001.py` |

以上短文件名均位于 `next-experiment/`。多个版本采用 `runpy` 组合前序脚本，不能只拷贝单个最新文件；源码目录的顶层依赖链一并保留。

## 建议阅读的报告

- [三个参考工程的来源和边界](../reports/reference-three-projects-001.md)
- [设置/输入法的共同故障链](../reports/harmony-settings-inputmethod-030-review.md)
- [Binder 修复设计](../reports/native-binder-pid-031-design.md)
- [触控板与状态栏调查](../reports/native-touchpad-statusbar-032-review.md)
- [033 自动返回机制](../reports/native-unattended-033.md)
- [034 NEON 与实机阶段结果](../reports/native-render-034.md)
- [035 分阶段诊断](../reports/native-render-035.md)
- [GPU 管线设计](../reports/native-render-pipeline-036-design.md)
- [041 原始服务 GPU 结果](../reports/native-render-041.md)
- [当前菜单清理与手动组合](../reports/manual-gpu-041-boot-cleanup-001.md)

这些报告有意保留实验发生时的原文；已完成试验不能重复执行，也不能覆盖原编号的输出。报告引用的 JSON、二进制、日志和截图未发布，其原始证据保存在本地。

## 未完成

触控板实体点击/手势的完整验收、状态栏显示、设置及输入法的修复复测、长期稳定性、互动场景帧时分布和稳定 120 FPS。启动成功、库加载成功、独立像素测试成功与最终交互验收是不同层次。
