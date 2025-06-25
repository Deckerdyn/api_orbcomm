from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.usuario import UsuarioSchema
from ..auth.auth import get_current_user


# llamadas al modelo
from ..models import Usuario

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session
        

#GET
@router.get("/usuarios", response_model=List[UsuarioSchema])
async def get_usuarios(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(Usuario))
    usuarios = result.scalars().all()
    return usuarios

#POST
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/usuarios", response_model=UsuarioSchema)
async def create_usuario(
    usuario: UsuarioSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    usuario.password_hash = hash_password(usuario.password_hash)
    new_usuario = Usuario(**usuario.dict(exclude_unset=True))
    db.add(new_usuario)
    await db.commit()
    await db.refresh(new_usuario)
    return new_usuario

#PUT
@router.put("/usuarios/{id_usuario}", response_model=UsuarioSchema)
async def update_usuario(
    id_usuario: int,
    usuario: UsuarioSchema,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == id_usuario))
    usuario_db = result.scalars().first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrada")

    for key, value in usuario.dict(exclude_unset=True).items():
        setattr(usuario_db, key, value)

    await db.commit()
    await db.refresh(usuario_db)
    return usuario_db

#DELETE
@router.delete("/usuarios/{id_usuario}")
async def delete_usuario(
    id_usuario: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == id_usuario))
    usuario_db = result.scalars().first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrada")

    await db.delete(usuario_db)
    await db.commit()
    return {"detail": "Usuario eliminado"}

# @router.get("/usuarios/actualizar-passwords")
# async def actualizar_passwords(db: AsyncSession = Depends(get_db)):
#     stmt = select(Usuario).where(Usuario.id_usuario.in_([1, 2, 3]))
#     result = await db.execute(stmt)
#     usuarios = result.scalars().all()

#     if not usuarios:
#         return {"message": "No se encontraron usuarios para actualizar."}

#     for usuario in usuarios:
#         usuario.password_hash = hash_password("astidi2025")

#     await db.commit()
#     return {"message": "Contraseñas actualizadas correctamente"}

