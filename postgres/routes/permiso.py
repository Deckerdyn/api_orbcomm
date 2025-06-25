from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.permiso import PermisoSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import Permiso
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session


#GET
@router.get("/permisos", response_model=List[PermisoSchema])
async def get_permisos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Permiso))
    permisos = result.scalars().all()
    return permisos

#POST
@router.post("/permisos", response_model=PermisoSchema)
async def create_permisos(
    permiso: PermisoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_permiso = Permiso(**permiso.dict(exclude_unset=True))
    db.add(new_permiso)
    await db.commit()
    await db.refresh(new_permiso)
    return new_permiso

#PUT
@router.put("/permisos/{id_permiso}", response_model=PermisoSchema)
async def update_permisos(
    id_permiso: int, 
    permiso: PermisoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Permiso).where(Permiso.id_permiso == id_permiso))
    permiso_db = result.scalars().first()
    if not permiso_db:
        raise HTTPException(status_code=404, detail="Permiso no encontrada")

    for key, value in permiso.dict(exclude_unset=True).items():
        setattr(permiso_db, key, value)

    await db.commit()
    await db.refresh(permiso_db)
    return permiso_db

#DELETE
@router.delete("/permisos/{id_permiso}")
async def delete_permisos(
    id_permiso: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Permiso).where(Permiso.id_permiso == id_permiso))
    permiso_db = result.scalars().first()    
    if not permiso_db:
        raise HTTPException(status_code=404, detail="Permiso no encontrada")

    await db.delete(permiso_db)
    await db.commit()
    return {"detail": "Permiso eliminado"}