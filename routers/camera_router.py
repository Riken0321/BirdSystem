from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.camera import Camera
from services.camera_service import (
    create_camera, get_all_cameras, get_camera_by_id, update_camera, delete_camera
)

router = APIRouter(prefix="/camera", tags=["Camera"])

@router.post("/", response_model=dict)
async def add_camera(alias: str, map_location: str):
    camera = await create_camera(alias, map_location)
    return {"id": camera.id, "alias": camera.alias, "map_location": camera.map_location, "upload_count": camera.upload_count}

@router.get("/", response_model=List[dict])
async def list_cameras():
    cameras = await get_all_cameras()
    return [{"id": c.id, "alias": c.alias, "map_location": c.map_location, "upload_count": c.upload_count} for c in cameras]

@router.get("/{camera_id}", response_model=dict)
async def get_camera(camera_id: int):
    camera = await get_camera_by_id(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"id": camera.id, "alias": camera.alias, "map_location": camera.map_location, "upload_count": camera.upload_count}

@router.put("/{camera_id}", response_model=dict)
async def edit_camera(camera_id: int, alias: Optional[str] = None, map_location: Optional[str] = None, upload_count: Optional[int] = None):
    camera = await update_camera(camera_id, alias, map_location, upload_count)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"id": camera.id, "alias": camera.alias, "map_location": camera.map_location, "upload_count": camera.upload_count}

@router.delete("/{camera_id}", response_model=dict)
async def remove_camera(camera_id: int):
    success = await delete_camera(camera_id)
    if not success:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"result": "success"}