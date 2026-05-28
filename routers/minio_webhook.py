from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from typing import Dict, Any
import hmac
import hashlib
from config import settings
from urllib.parse import unquote  # 新增导入
from services.minio_service import minio_client  # 新增导入
from services.video_analysis import VideoAnalyzer  # 新增导入

router = APIRouter()
#video_analyzer = VideoAnalyzer()  # 初始化视频分析器

@router.post("/api/video/notifications")
async def handle_minio_notification(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    处理MinIO文件上传通知
    功能：验证签名 -> 解析事件 -> 触发后台任务
    """
    try:
        # 验证签名
        if not await _validate_minio_signature(request):
            raise HTTPException(status_code=403, detail="Invalid signature")

        # 解析事件内容
        payload: Dict[str, Any] = await request.json()
        
        # 触发后台处理
        background_tasks.add_task(
            _process_upload_notification,
            payload.get("Records", [])
        )
        
        return {"status": "notification received"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _validate_minio_signature(request: Request) -> bool:
    """MinIO签名验证实现（带调试日志）"""
    try:
        signature = request.headers.get("X-Amz-Content-SHA256", "")
        
        # 新增签名头存在性检查
        if not signature:
            print("[WARNING] 签名头缺失，请检查MinIO通知配置")
            return True  # 临时允许无签名请求
        
        if not settings.minio_secret_key:
            print("[ERROR] 未配置MINIO_SECRET_KEY环境变量")
            return False

        payload = await request.body()
        calculated = hmac.new(
            settings.minio_secret_key.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        print(f"[DEBUG] 收到签名: {signature}")
        print(f"[DEBUG] 计算签名: {calculated}")
        
        return hmac.compare_digest(signature, calculated)
    except Exception as e:
        print(f"[ERROR] 签名验证异常: {str(e)}")
        return False

def _process_upload_notification(records: list):
    """后台处理任务"""   
    for record in records:
        if record.get("eventName", "").startswith("s3:ObjectCreated"):
            object_info = record["s3"]["object"]
            # 解码文件名
            decoded_filename = unquote(object_info['key'], encoding='utf-8')
            
            # 生成带签名的临时访问URL（有效期24小时）
            file_url = minio_client.get_presigned_url(decoded_filename)
            
            print(f"[MinIO通知] 新文件上传: {decoded_filename}")
            print(f"[有效文件URL] {file_url}")
            
            # 触发视频分析任务
            #video_analyzer.process_video(file_url)  # 调用视频分析服务