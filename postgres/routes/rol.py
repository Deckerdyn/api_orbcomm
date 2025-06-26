from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.rol import RolSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import Rol
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/roles", response_model=List[RolSchema])
async def get_roles(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Rol))
    roles = result.scalars().all()
    return roles

#POST
@router.post("/roles", response_model=RolSchema)
async def create_roles(
    rol: RolSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_rol = Rol(**rol.dict(exclude_unset=True))
    db.add(new_rol)
    await db.commit()
    await db.refresh(new_rol)
    return new_rol

#PUT
@router.put("/roles/{id_rol}", response_model=RolSchema)
async def update_roles(
    id_rol: int, 
    rol: RolSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Rol).where(Rol.id_rol == id_rol))
    rol_db = result.scalars().first()
    if not rol_db:
        raise HTTPException(status_code=404, detail="Rol no encontrada")

    for key, value in rol.dict(exclude_unset=True).items():
        setattr(rol_db, key, value)

    await db.commit()
    await db.refresh(rol_db)
    return rol_db

#DELETE
@router.delete("/roles/{id_rol}")
async def delete_roles(
    id_rol: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Rol).where(Rol.id_rol == id_rol))
    rol_db = result.scalars().first()
    if not rol_db:
        raise HTTPException(status_code=404, detail="Rol no encontrada")

    await db.delete(rol_db)
    await db.commit()
    return {"detail": "Rol eliminado"}
