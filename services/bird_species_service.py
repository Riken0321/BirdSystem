from models.bird_species import BirdSpecies
from tortoise.exceptions import DoesNotExist
from typing import List, Optional
import pandas as pd

# 新增物种
async def create_bird_species(data: dict) -> BirdSpecies:
    return await BirdSpecies.create(**data)

# 查询所有物种
async def get_all_bird_species() -> List[BirdSpecies]:
    return await BirdSpecies.all()

# 根据ID查询物种
async def get_bird_species_by_id(species_id: int) -> Optional[BirdSpecies]:
    try:
        return await BirdSpecies.get(id=species_id)
    except DoesNotExist:
        return None

# 更新物种
async def update_bird_species(species_id: int, data: dict) -> Optional[BirdSpecies]:
    species = await get_bird_species_by_id(species_id)
    if not species:
        return None
    for k, v in data.items():
        setattr(species, k, v)
    await species.save()
    return species

# 删除物种
async def delete_bird_species(species_id: int) -> bool:
    species = await get_bird_species_by_id(species_id)
    if not species:
        return False
    await species.delete()
    return True

# 批量导入 Excel
async def import_bird_species_from_excel(file_path: str) -> int:
    df = pd.read_excel(file_path)
    count = 0
    for _, row in df.iterrows():
        data = row.to_dict()
        await BirdSpecies.create(**data)
        count += 1
    return count