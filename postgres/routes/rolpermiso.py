from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.rolpermiso import RolPermisoSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import RolPermiso
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/rolpermisos", response_model=List[RolPermisoSchema])
async def get_rolpermisos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RolPermiso))
    rolpermisos = result.scalars().all()
    return rolpermisos

#POST
@router.post("/rolpermisos", response_model=RolPermisoSchema)
async def create_rolpermisos(
    rolpermiso: RolPermisoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_rolpermiso = RolPermiso(**rolpermiso.dict(exclude_unset=True))
    db.add(new_rolpermiso)
    await db.commit()
    await db.refresh(new_rolpermiso)
    return new_rolpermiso

#PUT
@router.put("/rolpermisos/{id_rolpermiso}", response_model=RolPermisoSchema)
async def update_rolpermisos(
    id_rolpermiso: int, 
    rolpermiso: RolPermisoSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RolPermiso).where(RolPermiso.id_rolpermiso == id_rolpermiso))
    rolpermiso_db = result.scalars().first()
    if not rolpermiso_db:
        raise HTTPException(status_code=404, detail="RolPermiso no encontrada")

    for key, value in rolpermiso.dict(exclude_unset=True).items():
        setattr(rolpermiso_db, key, value)

    await db.commit()
    await db.refresh(rolpermiso_db)
    return rolpermiso_db

#DELETE
@router.delete("/rolpermisos/{id_rolpermiso}")
async def delete_rolpermisos(
    id_rolpermiso: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(RolPermiso).where(RolPermiso.id_rolpermiso == id_rolpermiso))
    rolpermiso_db = result.scalars().first()    
    if not rolpermiso_db:
        raise HTTPException(status_code=404, detail="RolPermiso no encontrada")

    await db.delete(rolpermiso_db)
    await db.commit()
    return {"detail": "RolPermiso eliminado"}