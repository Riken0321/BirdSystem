from tortoise.models import Model
from tortoise import fields

class UploadRecord(Model):
    id = fields.UUIDField(pk=True)  # 保持UUID主键类型
    filename = fields.CharField(max_length=255)
    total_size = fields.BigIntField()
    status = fields.CharField(max_length=20, default='pending')
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "upload_records"
        
    # 添加保存方法验证
    async def save(self, *args, **kwargs):
        await super().save(*args, **kwargs)

class ChunkRecord(Model):
    id = fields.UUIDField(pk=True)
    upload = fields.ForeignKeyField(
        "models.UploadRecord", 
        related_name="chunks",
        db_constraint=True,  # 显式启用外键约束
        on_delete=fields.CASCADE
    )
    chunk_number = fields.IntField()
    status = fields.CharField(max_length=20)
    created_at = fields.DatetimeField(auto_now_add=True)