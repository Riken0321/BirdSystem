from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from models.bird_species import BirdSpecies
from services.bird_species_service import (
    create_bird_species, get_all_bird_species, get_bird_species_by_id, update_bird_species, delete_bird_species, import_bird_species_from_excel
)
import shutil
import os

router = APIRouter(prefix="/bird_species", tags=["BirdSpecies"])

@router.post("/", response_model=dict)
async def add_bird_species(data: dict):
    species = await create_bird_species(data)
    return {"id": species.id}

@router.get("/", response_model=List[dict])
async def list_bird_species():
    species_list = await get_all_bird_species()
    return [{"id": s.id, "chinese_name": s.chinese_name, "english_name": s.english_name, "scientific_name": s.scientific_name, "bird_order": s.bird_order, "family": s.family, "residency_type": s.residency_type, "protection_level": s.protection_level} for s in species_list]

@router.get("/{species_id}", response_model=dict)
async def get_bird_species(species_id: int):
    species = await get_bird_species_by_id(species_id)
    if not species:
        raise HTTPException(status_code=404, detail="Bird species not found")
    return {"id": species.id, "chinese_name": species.chinese_name, "english_name": species.english_name, "scientific_name": species.scientific_name, "bird_order": species.bird_order, "family": species.family, "residency_type": species.residency_type, "protection_level": species.protection_level}

@router.put("/{species_id}", response_model=dict)
async def edit_bird_species(species_id: int, data: dict):
    species = await update_bird_species(species_id, data)
    if not species:
        raise HTTPException(status_code=404, detail="Bird species not found")
    return {"id": species.id}

@router.delete("/{species_id}", response_model=dict)
async def remove_bird_species(species_id: int):
    success = await delete_bird_species(species_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bird species not found")
    return {"result": "success"}

@router.post("/import_excel", response_model=dict)
async def import_excel(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    count = await import_bird_species_from_excel(temp_path)
    os.remove(temp_path)
    return {"imported": count}