# BirdSystem OpenHarmony + Cloud 实施规范（单文档交付版）

版本：v1.0  
日期：2026-04-10  
适用范围：QEMU 模拟采集 + 宿主机 Python 推理 + OpenHarmony 端实时展示  
文档目标：作为“让 AI 直接生成代码”的唯一输入规范

---

## 1. 背景与目标

当前项目需要从原有 Windows 工程演进为“端云协同”架构，且硬件不可用，采用 QEMU + 预标注数据集进行模拟采集与验证。

本阶段首要目标不是吞吐极限，而是：

1. 跑通端到端闭环。  
2. 对比云端预测与本地预标注，快速验证误差。  
3. 形成可持续迭代的工程结构。

---

## 2. 已冻结决策（必须遵守）

1. 数据源：`静态图像序列流（Image Sequence Stream）`。  
2. 数据集下发：通过 `hdc file send` 推送至 QEMU ` /data/service/el1/public/ `。  
3. 云端框架：`FastAPI`（异步 I/O）。  
4. 端侧网络：优先 OpenHarmony 原生网络能力（`@ohos.net.http` / Native Socket），不引入 libcurl。  
5. 协议：V1 使用 `JSON`（可读性和调试优先）。  
6. 闭环优先级：`实时 Overlay > 本地误差日志 > 事件上报`。  
7. 离线策略：断连缓存 + 恢复重传。  
8. 类别映射：云端统一维护，端侧只消费版本化映射。  
9. 开发策略：放弃 MinIO 视频链路，直接建设“QEMU图像 -> 云端推理 -> 误差回传”主链路。

---

## 3. 原项目功能解构（用于迁移映射）

### 3.1 Data I/O（数据传递）

- 文件分片上传与任务状态管理（现有 FastAPI 路由 + ORM）。
- MinIO 通知链路为历史残留，不作为新架构主路径。
- 前端存在上传组件，但与主大屏展示未形成真实业务闭环。

### 3.2 Inference Logic（模型推理）

- YOLO 推理已在脚本层验证（离线 `predict`）。
- 在线推理服务化在旧项目中不完整（部分服务实现缺失）。

### 3.3 Post-processing/UI（结果展示）

- Vue 可视化大屏能力完善，但主要由 mock 数据驱动。
- 实时推理结果叠加与 GT/Pred 对比逻辑尚未标准化。

---

## 4. 目标架构总览

```text
QEMU(OpenHarmony)
  ├─ 图像序列读取器 (C++)
  ├─ 采集调度/队列/缓存 (C++)
  ├─ HTTP请求封装 (OHOS原生网络)
  ├─ 结果解析与误差计算 (C++/ArkTS)
  └─ 实时Overlay与日志展示 (ArkTS)
              │
              │ HTTP + JSON (+ multipart image)
              ▼
Cloud Host (Python FastAPI)
  ├─ /api/v1/infer/frame
  ├─ /api/v1/meta/class-map
  ├─ /api/v1/health
  ├─ YOLO推理运行时
  ├─ 类别映射与模型版本管理
  └─ 推理结果存储/评估汇总（可选）
```

---

## 5. 新项目目录规范（强约束）

```text
BirdSystem-NG/
  contracts/
    json/
      infer-frame-request.schema.json
      infer-frame-response.schema.json
      class-map-response.schema.json

  cloud/
    app/
      main.py
      api/v1/
        infer_router.py
        meta_router.py
        health_router.py
      inference/
        runtime_yolo.py
        preprocess.py
        postprocess.py
      services/
        class_map_service.py
        result_service.py
      schemas/
        infer.py
        meta.py
      persistence/
        models.py
        repository.py
      config/
        settings.py
      utils/
        logger.py
        trace.py
    models/
      weights/
        best.pt
      labels/
        class_map.json
    tools/
      convert_labels.py
      eval_metrics.py

  ohos/
    entry/src/main/
      ets/
        pages/
          Index.ets
          ResultPage.ets
        components/
          OverlayCanvas.ets
          LogPanel.ets
        stores/
          InferenceStore.ets
        services/
          HttpService.ets
          RetryService.ets
          ClassMapService.ets
      cpp/
        CMakeLists.txt
        include/
          data/ImageSequenceReader.h
          data/GtLabelLoader.h
          queue/FrameQueue.h
          cache/OfflineStore.h
          protocol/JsonCodec.h
          eval/ErrorAnalyzer.h
        src/
          data/ImageSequenceReader.cpp
          data/GtLabelLoader.cpp
          queue/FrameQueue.cpp
          cache/OfflineStore.cpp
          protocol/JsonCodec.cpp
          eval/ErrorAnalyzer.cpp
          bridge/NapiBridge.cpp
    tools/
      push_dataset_to_qemu.ps1
      replay_controller.ps1

  docs/
    OHOS_CLOUD_IMPLEMENTATION_SPEC.md
```

---

## 6. 端云职责边界（必须明确）

## 6.1 云端 Python 保留不动/优先复用

1. YOLO 模型加载与推理调用。  
2. 模型版本和类别映射（class_map）管理。  
3. 推理 API、健康检查、结构化日志。  
4. 可选：结果入库、评估报表生成。

## 6.2 OpenHarmony 端必须重构

1. 图像序列采集模拟（替代真实摄像头）。  
2. 帧调度、发送队列、断网缓冲、重传状态机。  
3. 实时 Overlay 与本地 GT/Pred 差异呈现。  
4. 本地误差日志存储（SQLite 或 JSONL 文件）。

---

## 7. 数据集组织与推送规范

## 7.1 QEMU 内目录标准

```text
/data/service/el1/public/dataset/
  images/
    000001.jpg
    000002.jpg
  labels/
    000001.json
    000002.json
  meta/
    dataset_info.json
```

## 7.2 `dataset_info.json` 示例

```json
{
  "dataset_name": "defect_eval_v1",
  "class_map_version": "2026-04-10",
  "frame_rate_simulated": 5,
  "image_ext": ".jpg",
  "label_format": "json"
}
```

## 7.3 GT Label JSON（单帧）建议格式

```json
{
  "frame_id": 1,
  "width": 1280,
  "height": 720,
  "objects": [
    { "class_id": 3, "bbox_xyxy": [120, 80, 260, 220] },
    { "class_id": 5, "bbox_xyxy": [500, 300, 680, 560] }
  ]
}
```

---

## 8. API 合同（V1，JSON）

## 8.1 获取类别映射

`GET /api/v1/meta/class-map?version=latest`

响应：

```json
{
  "class_map_version": "2026-04-10",
  "classes": [
    { "id": 0, "name": "background" },
    { "id": 1, "name": "scratch" },
    { "id": 2, "name": "crack" }
  ]
}
```

## 8.2 单帧推理

`POST /api/v1/infer/frame`  
`Content-Type: multipart/form-data`

表单字段：
- `meta`：JSON 字符串
- `image`：二进制图片文件

`meta` 示例：

```json
{
  "protocol_version": "1.0",
  "device_id": "qemu_01",
  "session_id": "sess_20260410_001",
  "frame_id": 1024,
  "capture_ts_ms": 1775791200123,
  "image": {
    "width": 1280,
    "height": 720,
    "encoding": "jpeg"
  },
  "class_map_version": "2026-04-10",
  "gt_label": {
    "objects": [
      { "class_id": 2, "bbox_xyxy": [100, 120, 200, 260] }
    ]
  }
}
```

响应示例：

```json
{
  "trace_id": "5cd11fd4-446b-46a5-b6aa-8c5f99e6e5da",
  "device_id": "qemu_01",
  "frame_id": 1024,
  "model": {
    "name": "yolo_best",
    "version": "2026-04-10-r3"
  },
  "latency_ms": 36,
  "detections": [
    {
      "class_id": 2,
      "class_name": "crack",
      "score": 0.94,
      "bbox_xyxy": [98, 122, 205, 262]
    }
  ],
  "summary": {
    "count": 1
  }
}
```

## 8.3 健康检查

`GET /api/v1/health`

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "2026-04-10-r3"
}
```

---

## 9. 端侧状态机（离线缓冲与重传）

每帧记录状态：

- `NEW`：新采集未发送  
- `SENDING`：发送中  
- `ACKED`：收到有效响应  
- `RETRY_WAIT`：等待重试  
- `FAILED_LOCAL`：超过重试上限，留本地待人工/批量补传

状态迁移：

1. `NEW -> SENDING -> ACKED`（成功）  
2. `SENDING -> RETRY_WAIT -> SENDING`（失败重试）  
3. 重试超限：`SENDING -> FAILED_LOCAL`  
4. 网络恢复：`FAILED_LOCAL/NEW -> SENDING`

重试策略建议：

- 最大重试次数：`5`  
- 退避：`1s, 2s, 4s, 8s, 16s`  
- 超时：单请求 `3-5s`

---

## 10. 误差分析与 UI 展示规范

## 10.1 误差计算规则（V1）

1. 对每个 GT 框寻找同类最高 IoU 的预测框。  
2. `IoU >= 0.5 且 class_id一致` => `OK`。  
3. `IoU < 0.5 或 class_id不一致` => `WARN/FAIL`。  
4. 多目标按 Hungarian/贪心匹配均可，V1 允许贪心。

## 10.2 Overlay 颜色规范

- GT 框：绿色  
- Pred 框：蓝色  
- 错配框：红色  
- 文本：`GT:<id> Pred:<id> IoU:<x.xx>`

## 10.3 本地日志字段（JSONL）

```json
{
  "ts_ms": 1775791200123,
  "frame_id": 1024,
  "trace_id": "5cd11fd4-446b-46a5-b6aa-8c5f99e6e5da",
  "status": "WARN",
  "gt_count": 2,
  "pred_count": 1,
  "avg_iou": 0.43,
  "mismatch_count": 1,
  "network_state": "online"
}
```

---

## 11. 标签格式转换（必须提供工具）

由于数据集标签可能不是 YOLO 标准，云端必须提供：

- `tools/convert_labels.py`  
- 支持输入：自定义 JSON / COCO / 其他  
- 输出：推理评估统一格式（与第 7.3 节兼容）

要求：

1. 可批量转换。  
2. 转换报告包含失败样本列表。  
3. 映射 class_id 时必须绑定 `class_map_version`。

---

## 12. 安全与配置

1. 所有 API 需带 `X-Device-Id` 或 token（V1 可先设备白名单）。  
2. 云端配置通过环境变量：模型路径、置信度阈值、日志级别。  
3. 禁止在代码硬编码路径与密钥。  
4. 推理请求日志必须包含 `trace_id` 便于端云排障。

---

## 13. 性能与容量基线（V1）

1. 模拟帧率：`3~5 FPS`。  
2. 单帧端到端目标：`< 500ms`（含网络与推理）。  
3. 本地缓存容量：至少 `2000 帧` 元数据 + 图片索引。  
4. 云端单实例并发：先按 `20 req/s` 设计，后续压测扩展。

---

## 14. 验收标准（Definition of Done）

必须全部满足：

1. QEMU 可从指定目录按序读取图像并持续发送。  
2. 云端 `/api/v1/infer/frame` 可稳定返回结构化推理结果。  
3. 端侧实时显示 GT 与 Pred Overlay。  
4. 端侧可生成误差日志并可按 `WARN/FAIL` 过滤。  
5. 断网后缓存生效，恢复后自动重传并最终 `ACKED`。  
6. 类别映射版本可被端侧拉取并用于解释结果。  
7. 提供至少 1 份评估报告（准确率/召回率/误差样例）。

---

## 15. 实施里程碑（建议）

### M1：最小可运行链路
- 完成单帧上传 + 云端返回 + 端侧打印结果。

### M2：可视化闭环
- Overlay 实时显示 + 本地误差日志。

### M3：容错与稳定
- 离线缓存、重传、状态机完成并压测。

### M4：评估自动化
- 批量回放 + 指标统计 + 错误样本导出。

---

## 16. 给“代码生成 AI”的执行指令模板（可直接复制）

你现在是该项目实现工程师，请严格按本规范实现，不得偏离以下约束：

1. 按第 5 节目录创建工程骨架。  
2. 先实现第 8 节 API 合同（FastAPI）。  
3. 再实现端侧图像序列读取、发送、结果展示、误差日志。  
4. 实现第 9 节离线状态机和重传策略。  
5. 所有结构体/DTO 字段名必须与第 8、10 节一致。  
6. 每完成一个里程碑，输出可运行命令与验证步骤。  
7. 不实现 MinIO/webhook 历史链路。  
8. 所有路径、阈值、版本号必须配置化。  

---

## 17. 非目标（本阶段不做）

1. 不接入真实摄像头驱动。  
2. 不做 gRPC/Protobuf 主通道（留作后续性能优化）。  
3. 不做复杂多租户权限体系。  
4. 不做大规模分布式调度。

---

## 18. 结论

本规范已经将“数据输入、端云协议、职责边界、离线补传、误差闭环、验收标准”全部收敛。  
对方团队可直接以此文档驱动 AI 生成代码并分阶段落地，无需再依赖原项目的 MinIO 残缺链路。

