# 测试与风险分级

## 级别 1：仅源码，无设备操作

```sh
python -m unittest discover -s tools -p 'test_*.py'
python tools/verify_source_tree.py
```

这是默认的仓库检查。Git 索引的白名单、UTF-8 文本、512 KiB 单文件上限、二进制/常见凭据扫描、已跟踪 Python 语法会被检查；不执行历史脚本、不联网 SSH、不构建或运行系统镜像。自动扫描不能替代人工审查。

## 级别 2：本地算法与交叉编译

例如 `test-native-cursor-032.py`、`test-native-rotation-034.py` 使用真实像素算法及 ASan/UBSan，但需要既有 WSL、编译器和本机路径。`test-native-gpu-composer-041.py` / `test-native-gpu-formats-042.py` 构建 ARM64 测试；**编译通过不是硬件执行通过**。

## 级别 3：真实 GPU、离屏

`run-native-gpu-composer-test-041.py` 与 `run-native-gpu-formats-042.py` 是历史真机诊断：创建独立目录、在 Ubuntu 上用真实 FD690 比较 RGB 像素、旋转、裁剪/缩放、边角光标、隐藏、释放输入后的空闲重绘与上下文迁移。它们不 modeset，但会 SSH、上传并执行 ARM64 程序。已有编号不能重复运行。

这些测试以诊断 root 身份执行，不能单独证明 HarmonyOS 原始服务的 UID、链接器命名空间或桌面集成；041 后续原始服务启动另有证据。

## 级别 4：原始服务、真实显示、启动/退出

`run-native-autoreturn-*`、`run-native-original-*` 可能改变一次性启动并重启。033/034/035/041 的受控启动已完成，不能重跑或覆盖其日志。软件 420 秒返回保障不是硬件 watchdog，不能保证在内核完全卡死时恢复。

`retrieve-native-evidence-*` 将原始 LAB 分区以只读 `ro,noload` 挂载并退出后卸载；不能改为 fsck 或在原分区回放日志来取证。

## 实验隔离

- `install-*`、`cleanup-*`、`archive-*`、部分 `test-*` 有实际副作用，不能用通配符批量运行。
- 只在明确授权的目标环境使用 SELinux permissive，保留真实模式证据，不改变 Ubuntu 安全设置。
- 为每次新试验使用新编号/独立输出；哈希、文件存在性及保护条件失败时先调查，不能强行跳过。
- 面板刷新率、加载成功、合成阶段耗时、完整桌面、物理输入和长期交互 FPS 分别验收。
