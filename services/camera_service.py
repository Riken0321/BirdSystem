from models.camera import Camera
from tortoise.exceptions import DoesNotExist
from typing import List, Optional

# 新增摄像头
async def create_camera(alias: str, map_location: str) -> Camera:
    camera = await Camera.create(alias=alias, map_location=map_location)
    return camera

# 查询所有摄像头
async def get_all_cameras() -> List[Camera]:
    return await Camera.all()

# 根据ID查询摄像头
async def get_camera_by_id(camera_id: int) -> Optional[Camera]:
    try:
        return await Camera.get(id=camera_id)
    except DoesNotExist:
        return None

# 更新摄像头
async def update_camera(camera_id: int, alias: Optional[str] = None, map_location: Optional[str] = None, upload_count: Optional[int] = None) -> Optional[Camera]:
    camera = await get_camera_by_id(camera_id)
    if not camera:
        return None
    if alias is not None:
        camera.alias = alias
    if map_location is not None:
        camera.map_location = map_location
    if upload_count is not None:
        camera.upload_count = upload_count
    await camera.save()
    return camera

# 删除摄像头
async def delete_camera(camera_id: int) -> bool:
    camera = await get_camera_by_id(camera_id)
    if not camera:
        return False
    await camera.delete()
    return True