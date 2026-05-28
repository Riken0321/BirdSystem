import os
from ultralytics import YOLO
import torch
from ultralytics.nn.tasks import DetectionModel
from torch.nn.modules.container import Sequential

# Allow the required global classes
torch.serialization.add_safe_globals([DetectionModel, Sequential])

def train_yolo(data_yaml, model_path=None, epochs=100, imgsz=640, batch=16, device='cpu', **kwargs):
    if model_path:
        model = YOLO(model_path, weights_only=False)
    else:
        model = YOLO('yolov8n.pt', weights_only=False)
    # 可考虑添加以下改进
    try:
        results = model.train(data=data_yaml, epochs=epochs, imgsz=imgsz, batch=batch, device=device, patience=0, **kwargs)
    except Exception as e:
        print(f"训练出错: {str(e)}")
        raise
    return results

if __name__ == "__main__":
    model_path = None  # 或指定自定义权重/结构，如 "path/to/yolov8n.yaml"
    train_args = dict(
        data='save/my.yaml',
        epochs=3000,
        imgsz=640,
        device='cuda',
        batch=16,
        workers=4,
        patience=0,
        amp=True,
    )
    print(f"开始训练，数据配置: {train_args['data']}, 权重: {model_path or 'yolov8n.pt (默认)'}")
    train_yolo(model_path=model_path, **train_args)
    print("训练完成！")