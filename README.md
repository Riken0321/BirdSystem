# BirdSystem

**鸟类智能监测与识别平台** — Vue3 可视化大屏、FastAPI 后端与 YOLOv8 离线训练流水线。

**GitHub**：https://github.com/Riken0321/BirdSystem

## 功能概览

- 鸟类监测 **数据大屏**（物种分布、时间动态、组成分析等）
- **FastAPI** 后端：用户认证、分片上传、物种/相机管理
- **YOLOv8** 离线训练与推理：视频抽帧 → 标注数据集 → 训练 → `best.pt` 检测

## 快速开始

### 前端（仅需预览大屏 UI）

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173 （当前为 Mock 数据，无需后端）

### 后端（可选）

```bash
pip install -r requirements.txt
cp .env.example .env   # 编辑数据库与 JWT 配置
uvicorn main:app --reload --port 8000
```

物种/相机 API 需启动备用入口：`uvicorn backend.main:app --reload --port 8001`

### 模型训练（离线）

```bash
pip install ultralytics torch opencv-python
python video_to_frames.py   # 可选：视频抽帧
python train.py             # 需配置 save/my.yaml 数据集
python test/main.py         # 推理验证（需 best.pt）
```

## 文档

详细架构、API 说明与 **鸟类 YOLO 训练全流程** 见：

**[PROJECT_ARCHITECTURE.md](./PROJECT_ARCHITECTURE.md)**

端云演进规范：[OHOS_CLOUD_IMPLEMENTATION_SPEC.md](./OHOS_CLOUD_IMPLEMENTATION_SPEC.md)

## 技术栈

Vue 3 · Vite · ECharts · FastAPI · Tortoise ORM · MySQL · Ultralytics YOLOv8

## 许可证

暂未添加 LICENSE 文件。
