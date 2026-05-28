import os
import os
from ultralytics import YOLO


# 定义模型路径，使用train2训练的最佳模型
model_path = 'd:/BirdSystem/runs/detect/train/weights/best.pt'

# 定义测试图片路径，假设用户会将测试图片放在test目录下
# 请将 'test_image.jpg' 替换为您实际的图片文件名
image_path = 'd:/BirdSystem/test/frame_000000.jpg'

# 检查测试图片是否存在
if not os.path.exists(image_path):
    print(f"错误：未找到测试图片 '{image_path}'。请将测试图片放入 'd:/BirdSystem/test/' 目录下并确保文件名正确。")
else:
    try:
        # 加载模型
        model = YOLO(model_path)

        # 对图片进行推理
        # save=True 会将结果保存到 runs/detect/predict 目录下
        results = model.predict(source=image_path, save=True, conf=0.01, iou=0.1)

        print(f"推理完成。结果已保存到 'runs/detect/predict' 目录下。请检查该目录下的图片以查看模型检测结果。")

        # 打印检测到的对象信息（可选）
        for r in results:
            if r.boxes:
                print(f"在图片 '{image_path}' 中检测到以下对象：")
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    print(f"  类别: {model.names[cls]}, 置信度: {conf:.2f}, 边界框: {xyxy}")
            else:
                print(f"在图片 '{image_path}' 中未检测到任何对象。")

    except Exception as e:
        print(f"执行推理时发生错误: {e}")