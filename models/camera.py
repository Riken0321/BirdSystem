from tortoise.models import Model
from tortoise import fields

class Camera(Model):
    id = fields.IntField(pk=True, description="主键ID")
    alias = fields.CharField(max_length=100, description="摄像头别名")
    map_location = fields.CharField(max_length=255, description="地图位置")
    upload_count = fields.IntField(default=0, description="上传次数")

    class Meta:
        table = "camera"
        table_description = "摄像头信息表"