from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from ..database import Base
import enum
from datetime import datetime


# class EstadoEnum(enum.Enum):
#     activo = "activo"
#     inactivo = "inactivo"

# class RolEnum(enum.Enum):
#     admin = "admin"
#     usuario = "usuario"

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    # rol = Column(Enum(RolEnum), default=RolEnum.admin)
    estado = Column(String , default="activo")

    # Referencias foreign keys -> hijos
    conductores = relationship("Conductor", back_populates="usuario")
    usuario_rol = relationship("UsuarioRol", back_populates="usuario")
