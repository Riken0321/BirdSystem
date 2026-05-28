# BirdSystem 项目架构解析文档

> 鸟类智能监测与识别平台 — 架构说明、模块职责与 YOLO 训练全流程指南

---

## 1. 项目简介

**BirdSystem** 是一套面向鸟类监测与识别的全栈工程，涵盖：

- **前端**：Vue 3 + Vite 可视化监测大屏（物种分布、时间动态、物种组成等）
- **后端**：FastAPI + Tortoise ORM + MySQL（用户认证、分片上传、物种/相机管理）
- **机器学习**：基于 Ultralytics **YOLOv8** 的离线训练与推理流水线（检测鸟类目标）

当前阶段，大屏主要由 **本地 Mock 数据** 驱动；模型训练为 **命令行离线流程**，尚未提供 HTTP 训练接口，也未与前端 UI 打通。未来演进方向见 [OHOS_CLOUD_IMPLEMENTATION_SPEC.md](./OHOS_CLOUD_IMPLEMENTATION_SPEC.md)（OpenHarmony 端云协同、在线推理 API）。

---

## 2. 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3、Vite 6、Tailwind CSS、ECharts、Axios | 数据大屏与分片上传组件 |
| 后端 | FastAPI、Tortoise ORM、aiomysql、JWT | 双入口应用（见下文） |
| 存储 | MySQL、MinIO（设计上有，部分服务未实现） | `.env` 配置 |
| ML | Ultralytics YOLOv8、PyTorch、OpenCV | 离线训练/推理，需单独安装 |
| 迁移 | Aerich | 数据库 schema 迁移 |

**Web 依赖**：见 [requirements.txt](./requirements.txt)  
**ML 依赖**（示例，需单独安装）：

```text
ultralytics>=8.0.0
torch
opencv-python
```

---

## 3. 目录结构

```text
BirdSystem/
├── frontend/                 # Vue3 前端（Vite，默认端口 5173）
│   └── src/
│       ├── App.vue           # 监测大屏主界面
│       ├── main.js           # Axios 基址配置
│       └── components/       # 图表、上传等组件
├── main.py                   # 主 FastAPI 入口（认证、上传、Webhook）
├── backend/
│   └── main.py               # 备用 FastAPI 入口（相机、物种 CRUD）
├── routers/                  # API 路由
├── models/                   # Tortoise ORM 模型（物种、检测记录、相机等）
├── services/                 # 业务服务层
├── middlewares/              # 日志、认证中间件
├── migrations/               # Aerich 数据库迁移
├── utils/                    # JWT、日志工具
├── config.py                 # ORM 与全局配置
├── train.py                  # YOLOv8 训练脚本
├── video_to_frames.py        # 视频抽帧工具
├── test/main.py              # YOLO 离线推理测试
├── runs/detect/              # 训练产物（权重不提交 Git）
├── requirements.txt
├── .env.example              # 环境变量模板（勿提交真实 .env）
├── OHOS_CLOUD_IMPLEMENTATION_SPEC.md  # 端云演进规范
└── PROJECT_ARCHITECTURE.md   # 本文档
```

---

## 4. 系统架构

### 4.1 整体分层图

```mermaid
flowchart TB
  subgraph frontend [Frontend Vue3 Vite]
    AppVue[App.vue 监测大屏]
    Mock[generateMockData 本地 Mock]
    Upload[FileUploader 分片上传 未挂载]
  end

  subgraph backendRoot [main.py 根入口 :8000]
    Auth["/token 认证"]
    UploadAPI["/api/upload 分片上传"]
    Webhook["/api/video/notifications"]
  end

  subgraph backendAlt [backend/main.py 备用入口]
    Species["/bird_species 物种 CRUD"]
    Camera["/cameras 相机"]
  end

  subgraph ml [离线 ML 支路]
    Frames[video_to_frames.py]
    Train[train.py YOLOv8]
    Runs[runs/detect 训练产物]
    Infer[test/main.py predict]
  end

  DB[(MySQL via Tortoise ORM)]

  AppVue --> Mock
  Upload -.->|设计目标| UploadAPI
  frontend -.->|axios baseURL| backendRoot
  backendRoot --> DB
  backendAlt --> DB
  Frames --> Train --> Runs --> Infer
```

### 4.2 双后端入口（重要）

项目存在 **两个独立的 FastAPI 应用**，功能未合并，启动时请勿混淆：

| 入口 | 文件 | 建议端口 | 已注册能力 |
|------|------|----------|------------|
| **主应用** | `main.py` | 8000 | `/token` 认证、`/users/*` 用户、`/api/upload/*` 分片上传、`/api/video/notifications` MinIO Webhook |
| **备用应用** | `backend/main.py` | 8001 | 用户 CRUD、`/cameras` 相机、`/bird_species` 物种（含 Excel 导入） |

启动示例：

```bash
# 主应用
cd BirdSystem
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 备用应用（需另开终端，避免端口冲突）
uvicorn backend.main:app --reload --port 8001
```

主应用使用 `config.TORTOISE_ORM` 与 `.env`；备用应用内硬编码了 `mysql://root:123456@localhost/mydatabase`，生产环境应统一为环境变量配置。

---

## 5. 后端 API 与数据模型

### 5.1 主要路由（按入口）

**根 `main.py`**

| 前缀 | 模块 | 说明 |
|------|------|------|
| `/token` | `routers/auth_router.py` | OAuth2 登录，返回 JWT |
| `/users/` | `routers/user_router.py` | 用户 CRUD |
| `/api/upload/` | `routers/upload_router.py` | 分片上传至 MinIO |
| `/api/video/notifications` | `routers/minio_webhook.py` | MinIO 事件回调 |

**`backend/main.py`**

| 前缀 | 模块 | 说明 |
|------|------|------|
| `/bird_species/` | `routers/bird_species_router.py` | 鸟类物种增删改查、Excel 导入 |
| 相机相关 | `routers/camera_router.py` | 相机设备管理 |

### 5.2 核心数据模型

**`models/bird_species.py`**

- **`BirdSpecies`**：物种信息表。字段含中文名、英文名、学名、目/科、居留类型、保护级别等。注释标明 **`id` 同时可作为 YOLO 训练时的类别 ID**，用于将检测结果映射到业务物种。
- **`DetectionRecord`**：检测记录（视频 URL、帧号、物种 ID、置信度、时间戳）。模型已定义，但 **尚无对应 Router/Service 写入接口**。

### 5.3 已知后端缺口

| 问题 | 影响 |
|------|------|
| `services/minio_service.py` 缺失 | `upload_router`、`minio_webhook` 无法正常 import，主应用上传链路不可用 |
| `services/video_analysis.py` 缺失 | Webhook 中视频分析未接通 |
| 双 `main.py` 功能分裂 | 同一前端无法通过一个端口访问全部 API |
| 在线推理 `/api/v1/infer/frame` | 仅在 OHOS 规范中规划，代码未实现 |

---

## 6. 鸟类检测模型训练完整指南

> **核心结论**：训练鸟（鸟类目标检测）功能是 **离线 CLI 流水线**，不经过 Web API，也不在前端界面操作。

### 6.1 训练流程总览

```mermaid
flowchart LR
  A[原始视频或图片] --> B[video_to_frames.py 抽帧]
  B --> C[标注与 YOLO 数据集 my.yaml]
  C --> D[train.py ultralytics.train]
  D --> E[runs/detect/train/weights/best.pt]
  E --> F[test/main.py predict]
  F --> G[runs/detect/predict 可视化结果]
```

### 6.2 步骤详解

#### 步骤 1：视频抽帧（可选）

若数据源为视频，使用 `video_to_frames.py` 将视频导出为逐帧图片：

```bash
python video_to_frames.py
```

脚本使用 OpenCV `cv2.VideoCapture` 读取视频，按 `frame_interval` 间隔保存为 `frame_XXXXXX.jpg`。输出目录需在脚本 `__main__` 中配置 `video_path` 与 `output_folder`。

#### 步骤 2：数据标注与 YOLO 数据集配置

1. 将图片放入 YOLO 标准目录结构，例如：

```text
dataset/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/    # 与 images 同名的 .txt 标注（class x_center y_center w h，归一化）
    └── val/
```

2. 编写数据集 YAML（如 `save/my.yaml` 或历史路径 `D:\save\1\my.yaml`），示例：

```yaml
path: D:/your_dataset_root
train: images/train
val: images/val
names:
  0: sparrow
  1: magpie
  # ... 鸟类类别，索引需与 BirdSpecies.id 对齐（设计约定）
```

历史训练记录见 `runs/detect/train/args.yaml`，其中 `data: D:\save\1\my.yaml`、`model: D:\save\1\yolov8n.yaml`。

#### 步骤 3：执行训练

使用 `train.py` 封装 Ultralytics 训练：

```python
from train import train_yolo

train_yolo(
    data_yaml="save/my.yaml",      # 数据集配置路径
    model_path=None,               # None 则使用 yolov8n.pt 预训练权重
    epochs=100,
    imgsz=640,
    batch=16,
    device="cuda",                 # 或 "cpu"
)
```

或直接运行（需先修正 `data` 路径与 GPU 环境）：

```bash
python train.py
```

`train_yolo()` 内部调用：

```python
model = YOLO(model_path or "yolov8n.pt")
results = model.train(data=data_yaml, epochs=epochs, imgsz=imgsz, batch=batch, device=device, patience=0, **kwargs)
```

训练产物默认写入 `runs/detect/train/`（或 `train2/` 等），包含：

- `weights/best.pt` — 验证集最优权重（**体积大，不提交 Git**）
- `results.csv` — 训练指标曲线
- `args.yaml` — 本次训练参数快照

#### 步骤 4：离线推理验证

编辑 `test/main.py` 中的路径后执行：

```bash
python test/main.py
```

- **模型**：`runs/detect/train/weights/best.pt`
- **测试图**：`test/frame_000000.jpg`
- **输出**：`runs/detect/predict/` 下带检测框的可视化图片

推理使用 `model.predict(source=..., save=True, conf=0.01, iou=0.1)`，控制台会打印类别名、置信度与边界框。

#### 步骤 5：与业务系统关联（设计层）

| 概念 | 说明 |
|------|------|
| 类别 ID | YOLO `names` 字典中的索引，设计上可与 `BirdSpecies.id` 一致 |
| 检测记录 | `DetectionRecord` 表用于存储视频 URL、帧号、物种 ID、置信度；待在线推理 API 实现后写入 |
| 在线推理 | 规划为 `POST /api/v1/infer/frame`（见 OHOS 规范），当前 **未实现** |

### 6.3 训练参数参考

根据 `runs/detect/train/args.yaml` 历史记录，项目曾使用：

| 参数 | 典型值 |
|------|--------|
| model | yolov8n（轻量检测头） |
| epochs | 3000（长训；可按数据量调整） |
| imgsz | 640 |
| batch | 16（或 -1 自动） |
| device | CUDA GPU |
| amp | true（混合精度） |

### 6.4 排错与限制

| 现象 | 原因与处理 |
|------|------------|
| `train.py` 报 `train_args` / `model_path` 未定义 | 已修复：移除模块级过早的 `select_device`，`__main__` 中显式设置 `model_path=None` |
| 找不到 `save/my.yaml` | 数据集配置在仓库外，需自行创建 `save/` 或修改 `data` 路径 |
| `test/main.py` 找不到 `best.pt` | 需先完成训练，或将 `model_path` 指向已有权重 |
| 上传/分析不可用 | `minio_service` 未实现，与训练流水线无关 |

---

## 7. 前端说明

### 7.1 启动

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：**http://localhost:5173**

### 7.2 架构要点

| 文件 | 职责 |
|------|------|
| `src/App.vue` | 监测大屏：地图、KPI、物种组成、时间动态等 |
| `src/main.js` | `axios.defaults.baseURL = VITE_API_URL \|\| http://localhost:8000` |
| `components/FileUploader.vue` | 分片上传（对接 `/api/upload/*`），**未挂载到 App 模板** |
| `components/UploadForm.vue` | 上传表单壳，未接后端 |
| `components/*.vue` | ECharts 子图表组件 |

大屏数据由 `generateMockData()` 生成，**无需后端即可预览 UI**。接入真实 API 需替换 Mock 并挂载上传/登录组件。

### 7.3 环境变量

在 `frontend/.env` 中可设置：

```env
VITE_API_URL=http://localhost:8000
```

---

## 8. 本地开发与端口一览

| 服务 | 命令 | 端口 |
|------|------|------|
| 前端 | `cd frontend && npm run dev` | 5173 |
| 主后端 | `uvicorn main:app --reload --port 8000` | 8000 |
| 备用后端 | `uvicorn backend.main:app --reload --port 8001` | 8001 |
| MySQL | 按 `.env` 中 `DB_URL` | 3306 |
| MinIO | 按 `.env` 中 `MINIO_ENDPOINT` | 9000 |

环境变量模板见 [.env.example](./.env.example)。

---

## 9. 演进规划与参考文档

- **[OHOS_CLOUD_IMPLEMENTATION_SPEC.md](./OHOS_CLOUD_IMPLEMENTATION_SPEC.md)**：描述 QEMU + OpenHarmony 采集、云端 FastAPI 推理、`/api/v1/infer/frame` 等目标架构；与当前仓库代码存在差距，实施时以该文档为契约参考。
- **弃用方向**：MinIO 视频分析主链路在新规范中降级，优先建设「图像序列 → 云端推理 → 误差回传」闭环。

---

## 10. 许可证与贡献

当前仓库 **暂未添加 LICENSE 文件**。如需开源协作，建议补充 MIT/Apache-2.0 等许可证后再对外分发。

贡献前请注意：勿提交 `.env`、`*.pt` 权重、`venv/`、`node_modules/` 等大文件或敏感信息。

---

*文档版本：与仓库初始公开 release 同步*
