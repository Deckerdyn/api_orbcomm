from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.usuariorol import UsuarioRolSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import UsuarioRol
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

#GET
@router.get("/usuariorol", response_model=List[UsuarioRolSchema])
async def get_usuariorols(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(UsuarioRol))
    usuariorols = result.scalars().all()
    return usuariorols

#POST
@router.post("/usuariorol", response_model=UsuarioRolSchema)
async def create_usuariorols(
    usuariorol: UsuarioRolSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_usuariorol = UsuarioRol(**usuariorol.dict(exclude_unset=True))
    db.add(new_usuariorol)
    await db.commit()
    await db.refresh(new_usuariorol)
    return new_usuariorol

#PUT
@router.put("/usuariorol/{id_usuariorol}", response_model=UsuarioRolSchema)
async def update_usuariorols(
    id_usuariorol: int, 
    usuariorol: UsuarioRolSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(UsuarioRol).where(UsuarioRol.id_usuariorol == id_usuariorol))
    usuariorol_db = result.scalars().first()
    if not usuariorol_db:
        raise HTTPException(status_code=404, detail="UsuarioRol no encontrada")

    for key, value in usuariorol.dict(exclude_unset=True).items():
        setattr(usuariorol_db, key, value)

    await db.commit()
    await db.refresh(usuariorol_db)
    return usuariorol_db

#DELETE
@router.delete("/usuariorol/{id_usuariorol}")
async def delete_usuariorols(
    id_usuariorol: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(UsuarioRol).where(UsuarioRol.id_usuariorol == id_usuariorol))
    usuariorol_db = result.scalars().first()    
    if not usuariorol_db:
        raise HTTPException(status_code=404, detail="UsuarioRol no encontrada")

    await db.delete(usuariorol_db)
    await db.commit()
    return {"detail": "UsuarioRol eliminado"}