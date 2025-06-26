from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from geoalchemy2.shape import to_shape
from ..database import SessionLocal
from ..schemas.paradasautorizadas import ParadasAutorizadasSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import ParadasAutorizadas
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/paradasautorizadas", response_model=List[ParadasAutorizadasSchema])
async def get_paradasautorizadas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(ParadasAutorizadas))
    paradas_autorizadas = result.scalars().all()
    return paradas_autorizadas


# @router.get("/paradasautorizadas", response_model=List[ParadasAutorizadasSchema])
# async def get_paradasautorizadas(
#     db: AsyncSession = Depends(get_db),
#     current_user: Usuario = proteccion_user
#     ):
#     result = await db.execute(select(ParadasAutorizadas))
#     paradas_raw = result.scalars().all()

#     paradas_serializadas = []
#     for parada in paradas_raw:
#         parada_dict = parada.__dict__.copy()
#         if parada.geom:
#             shape = to_shape(parada.geom)
#             parada_dict["geom"] = shape.wkt
#         else:
#             parada_dict["geom"] = None
#         paradas_serializadas.append(ParadasAutorizadasSchema(**parada_dict))

#     return paradas_serializadas

#POST
@router.post("/paradasautorizadas", response_model=ParadasAutorizadasSchema)
async def create_paradasautorizadas(
    paradasautorizadas: ParadasAutorizadasSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_paradasautorizadas = ParadasAutorizadas(**paradasautorizadas.dict())
    db.add(new_paradasautorizadas)
    await db.commit()
    await db.refresh(new_paradasautorizadas)
    return new_paradasautorizadas

#PUT
@router.put("/paradasautorizadas/{id_paradasautorizadas}", response_model=ParadasAutorizadasSchema)
async def update_paradasautorizadas(
    id_paradasautorizadas: int, 
    paradasautorizadas: ParadasAutorizadasSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(ParadasAutorizadas).where(ParadasAutorizadas.id_paradasautorizadas == id_paradasautorizadas))
    paradasautorizadas_db = result.scalars().first()
    if not paradasautorizadas_db:
        raise HTTPException(status_code=404, detail="ParadasAutorizadas no encontrada")

    for key, value in paradasautorizadas.dict(exclude_unset=True).items():
        setattr(paradasautorizadas_db, key, value)

    await db.commit()
    await db.refresh(paradasautorizadas_db)
    return paradasautorizadas_db

#DELETE
@router.delete("/paradasautorizadas/{id_paradasautorizadas}")
async def delete_paradasautorizadas(
    id_paradasautorizadas: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(ParadasAutorizadas).where(ParadasAutorizadas.id_paradasautorizadas == id_paradasautorizadas))
    paradasautorizadas_db = result.scalars().first()
    if not paradasautorizadas_db:
        raise HTTPException(status_code=404, detail="ParadasAutorizadas no encontrada")

    await db.delete(paradasautorizadas_db)
    await db.commit()    
    return {"detail": "ParadasAutorizadas eliminado"}