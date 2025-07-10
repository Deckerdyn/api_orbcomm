from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import SessionLocal
from ..schemas.usuario import UsuarioSchema, UsuarioCreateSchema, UsuarioUpdateSchema
from ..auth.auth import get_current_user


# llamadas al modelo
from ..models import Usuario
from ..models import Conductor #Importamos para obtener los usuarios sin conductor

router = APIRouter()
proteccion_user = Depends(get_current_user) # Proteccion rutas

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session
  

# GET Usuarios que no han sido asignados a conductores
@router.get("/usuarios/sin-conductor")
async def get_usuarios_sin_conductor(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas
    ):
    # Subconsulta para obtener todos los id_usuario de conductores
    subq = select(Conductor.id_usuario)

    # Buscar usuarios cuyo id no esté en esa lista
    result = await db.execute(
        select(Usuario).where(Usuario.id_usuario.not_in(subq))
    )
    
    usuarios = result.scalars().all()
    
    # si es vacío, devuelve None
    if not usuarios:
        return {
                "data": None,
                "res" : False,
                "msg": "Todos los usuarios tienen conductor asignado"
            }
    
    return {
            "data": usuarios,
            "res" : True,
            "msg": "Usuarios sin conductor obtenido correctamente"
        }      

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

@router.post("/usuarios")
async def create_usuario(
    usuario: UsuarioCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user # Proteccion rutas 
    ):
    usuario.password_hash = hash_password(usuario.password_hash)
    new_usuario = Usuario(**usuario.dict(exclude_unset=True))
    db.add(new_usuario)
    await db.commit()
    await db.refresh(new_usuario)
    return {
        "data": new_usuario,
        "res" : True,
        "msg": "Usuario creado correctamente"
    }

#PUT
@router.put("/usuarios/{id_usuario}")
async def update_usuario(
    id_usuario: int,
    usuario: UsuarioUpdateSchema,
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
    return {
            "data": usuario_db,
            "res" : True,
            "msg": "Usuario actualizado correctamente"
        }

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
    return {
            "data": None,
            "res" : True,
            "msg": "Usuario eliminado"
        }

# GET especifico usuario
@router.get("/usuarios/{id_usuario}")
async def get_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = proteccion_user
    ):
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == id_usuario))
    usuario_db = result.scalars().first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "data": usuario_db,
        "res" : True,
        "msg": "Usuario obtenido correctamente"
    }
    


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

