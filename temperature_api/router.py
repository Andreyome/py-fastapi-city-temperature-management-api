from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from . import crud
from temperature_api import schemas

router = APIRouter()


@router.get("/temperatures/", response_model=list[schemas.TemperatureSchema])
async def get_temperature(db: AsyncSession = Depends(get_db)):
    return await crud.get_temperature_list(db=db)


@router.get("/temperatures/{city_id}/", response_model=list[schemas.TemperatureSchema])
async def get_temperature_by_city_id(city_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_temperature_by_city_id(db=db, city_id=city_id)
