from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.empresa import EmpresaSchema, EmpresaCreateSchema, EmpresaUpdateSchema
from ..auth.auth import get_current_user #Importamos para proteccion de rutas

# llamadas al modelo
from ..models import Empresa
from ..models import Usuario #importamos para proteccion de rutas

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/empresas", response_model=List[EmpresaSchema])
async def get_empresas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Empresa))
    empresas = result.scalars().all()
    return empresas

@router.post("/empresas", response_model=EmpresaSchema)
async def create_empresa(
    empresa: EmpresaCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    new_empresa = Empresa(**empresa.dict(exclude_unset=True))
    db.add(new_empresa)
    await db.commit()
    await db.refresh(new_empresa)
    return new_empresa

@router.put("/empresas/{id_empresa}", response_model=EmpresaSchema)
async def update_empresa(
    id_empresa: int, 
    empresa: EmpresaUpdateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Empresa).where(Empresa.id_empresa == id_empresa))
    empresa_db = result.scalars().first()
    if not empresa_db:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    for key, value in empresa.dict(exclude_unset=True).items():
        setattr(empresa_db, key, value)

    await db.commit()
    await db.refresh(empresa_db)
    return empresa_db

@router.delete("/empresas/{id_empresa}")
async def delete_empresa(
    id_empresa: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Empresa).where(Empresa.id_empresa == id_empresa))
    empresa_db = result.scalars().first()
    if not empresa_db:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    await db.delete(empresa_db)
    await db.commit()
    return {"detail": "Empresa eliminada"}

#GET especifico empresa
@router.get("/empresas/{id_empresa}", response_model=EmpresaSchema)
async def get_empresa(
    id_empresa: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Empresa).where(Empresa.id_empresa == id_empresa))
    empresa_db = result.scalars().first()
    if not empresa_db:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return empresa_db