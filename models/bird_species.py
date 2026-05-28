from tortoise.models import Model
from tortoise import fields
from typing import List, Dict, Any

# 物种表
class BirdSpecies(Model):
    id = fields.IntField(pk=True, description="主键ID,也是训练的ID")
    chinese_name = fields.CharField(max_length=100, description="中文名")
    english_name = fields.CharField(max_length=100, description="英文名")
    scientific_name = fields.CharField(max_length=150, description="学名")
    bird_order = fields.CharField(max_length=50, db_column="bird_order", description="目")  # 避免使用order保留字
    family = fields.CharField(max_length=50, description="科")
    residency_type = fields.CharField(max_length=20,null=True,description="居留类型（留/（春/夏/秋/冬）/旅）")
    protection_level = fields.CharField(max_length=10,null=True,description="保护级别（国家一级/国家二级/三有动物）")

    class Meta:
        table = "bird_species"
        table_description = "鸟类物种信息表"

class DetectionRecord(Model):
    """鸟类检测记录模型"""
    id = fields.UUIDField(pk=True, description="主键UUID")
    video_url = fields.CharField(max_length=500, description="视频文件地址")
    frame_number = fields.IntField(description="检测帧序号")
    species_id = fields.IntField(description="物种分类ID")
    confidence = fields.FloatField(description="检测置信度")
    timestamp = fields.DatetimeField(auto_now_add=True, description="检测时间戳")
    class Meta:
        table = "detection_records"
        indexes = [
            ("video_url", "frame_number"),  # 视频+帧号联合索引
            ("species_id", "timestamp")     # 物种+时间索引
        ]
    def __str__(self):
        return f"{self.timestamp} 检测到物种 {self.species_id} (置信度: {self.confidence:.2f})"

    @classmethod
    async def bulk_update(cls, update_data: List[Dict[str, Any]]):
        """批量更新物种数据（事务方式）
        Args:
            update_data: 更新数据列表，格式 [{"id":1, "chinese_name":"树麻雀"},...]
        """
        async with in_transaction() as conn:
            for data in update_data:
                await cls.filter(id=data["id"]).using_db(conn).update(
                    chinese_name=data["chinese_name"]
                )