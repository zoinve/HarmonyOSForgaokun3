# 架构与数据流

## 原始服务链路

```text
原始应用 / SceneBoard / SystemUI
  → 原始 RenderService / NativeWindow / 队列
  → 匹配目标 ABI 的 EGL / Mesa Freedreno
  → 原始 display composer 服务 → 本项目 VDI 实现
  → DRM/KMS → DSI 面板
```

保留原始服务、身份、队列及回调语义，不以私有函数微测或模拟成功替代系统集成。平台工具链与 SDK C++ 标准库命名空间必须隔离。

## 041 GPU composer

1. 打开真实 render node，通过 GBM 分配两个线性、可渲染、可 scanout 的缓冲。
2. DMA-BUF 通过 PRIME 导入 KMS 文件描述符，并创建 framebuffer；不假定 DRM DUMB 缓冲一定能被 EGL 导入。
3. 等待真实输入 fence，将当前客户端 DMA-BUF 以其实际格式、pitch、裁剪范围导入 EGL。
4. 第一遍 shader 做裁剪/缩放/横屏旋转，写入 composer 自有背景纹理。
5. 第二遍从背景纹理叠加真实 MMI 光标，写入后台 scanout；真实 `glFinish` 完成后才翻页。
6. 空闲时移动/隐藏光标使用保留背景，无需重新读取已释放的客户端缓冲；同一互斥锁保护上下文在线程间的绑定/解绑。
7. GPU 初始化或帧处理失败如实记录，保留 034 NEON CPU 回退。当前同步策略优先正确性，后续才讨论进一步异步 fence 优化。

生命周期区分 KMS 导入的 GEM handle 与 GBM 所有权：前者使用 GEM_CLOSE，不能误用 DESTROY_DUMB。GL 对象、EGL image、映射、导出 FD、GBM BO 和 context 的释放顺序均需维护。

## 光标

原始 SDK 的特定光标 adapter 使用 emulator 实现，绘制和位置方法实际为空。适配器对审计过的 ABI 做严格校验，仅桥接绘制、位置、可见性三个槽位；其他行为委托原对象，ABI 不匹配时不强行改写。

MMI 发布真实坐标和原始可见性，composer 读取受所有者、组、权限、长度等约束的共享状态。没有注入鼠标事件、伪造 RS surface 或修改服务身份。CPU 与 GPU 路径均保留私有无光标背景，避免拖影。

## Binder

ACCESS_TOKENID 扩展原先把外层数值 PID 当作发送方 PID。031 对事务保留真实 TGID 引用，在接收方命名空间转换，并在正常/错误释放路径配对 `put_pid`。标准 Binder ABI、token 与权限检查不变；异步事务也不依赖可能为零的标准 sender 字段。

## 实测边界

035 揭示 CPU 路径约 14.9 ms 用于 DMA-BUF → RAM，单优化 NEON 不能消除该瓶颈。041 在原始 composer UID 3036 下有 GPU ready 与实际 GPU frame 双重证据，限定阶段均值约 4.15 ms。这个数字不包含所有应用绘制、GPU 提交、KMS 等待或交互开销；不能换算为桌面实际 FPS。
