import cv2
import os

def extract_frames(video_path, output_folder, frame_interval=1):
    """
    将视频分解成图片帧

    Args:
        video_path (str): 输入视频文件的路径
        output_folder (str): 输出图片帧的文件夹路径
        frame_interval (int, optional): 间隔多少帧提取一帧，默认每帧都提取
    """
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 按间隔提取帧
        if frame_count % frame_interval == 0:
            # 构建图片文件名
            frame_filename = os.path.join(output_folder, f"frame_{frame_count:06d}.jpg")
            # 保存图片
            cv2.imwrite(frame_filename, frame)
            print(f"已保存: {frame_filename} ({frame_count + 1}/{total_frames})")

        frame_count += 1

    # 释放视频捕获对象
    cap.release()
    print(f"共提取 {frame_count} 帧，保存到 {output_folder}")


# 示例用法
video_file = "./videos/input_video.mp4"  # 输入视频文件路径
output_dir = "output_frames"    # 输出图片文件夹路径
frame_interval = 10             # 每隔10帧提取一次（可以根据需要调整）

extract_frames(video_file, output_dir, frame_interval)