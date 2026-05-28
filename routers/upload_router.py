from fastapi import APIRouter, UploadFile, HTTPException
from services.minio_service import minio_client
from models.upload import UploadRecord, ChunkRecord
from pydantic import BaseModel, ValidationError

router = APIRouter(prefix="/api/upload", tags=["文件上传"])

class UploadInitRequest(BaseModel):
    filename: str
    total_size: int  # 保持蛇形命名与前端一致

@router.post("/init")
async def init_upload(request: UploadInitRequest):
    """初始化分片上传任务"""
    try:
        # 创建上传记录
        upload = await UploadRecord.create(
            filename=request.filename,
            total_size=request.total_size,
            status="pending"
        )
        return {"upload_id": str(upload.id)}
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="上传任务初始化失败"
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

@router.post("/chunk/{upload_id}/{chunk_number}")
async def upload_chunk(
    upload_id: str,
    chunk_number: int,
    file: UploadFile
):
    """上传文件分块"""
    # 添加分块序号验证
    if chunk_number < 1 or chunk_number > 1000:  # 假设最大1000个分块
        raise HTTPException(400, "无效的分块序号")
    
    # 添加分块大小验证（5MB）
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(413, "分块大小超过5MB限制")
    # 验证上传任务
    upload = await UploadRecord.get_or_none(id=upload_id)
    if not upload or upload.status != "pending":
        raise HTTPException(400, "无效的上传任务")
    
    # 保存分块记录
    await ChunkRecord.create(
        upload_id=upload_id,
        chunk_number=chunk_number,
        status="uploading"
    )
    
    # 调用MinIO服务上传分块
    success = await minio_client.upload_chunk(
        file.file,
        f"chunks/{upload_id}/{chunk_number}",  # 统一添加chunks前缀
        chunk_number
    )
    
    # 更新分块状态
    await ChunkRecord.filter(
        upload_id=upload_id,
        chunk_number=chunk_number
    ).update(status="success" if success else "failed")
    
    return {"status": "success" if success else "failed"}

@router.post("/complete/{upload_id}")
async def complete_upload(upload_id: str):
    """完成上传并合并分块"""
    upload = await UploadRecord.get(id=upload_id)
    success = await minio_client.merge_chunks(
        upload_id,
        upload.filename
    )
    
    # 合并成功后清理分片记录
    if success:
        # 删除关联的所有分片记录
        await ChunkRecord.filter(upload_id=upload_id).delete()
        # 更新主记录状态
        upload.status = "completed"
        await upload.save()
    else:
        upload.status = "failed"
        await upload.save()
    
    return {"status": "completed" if success else "failed"}