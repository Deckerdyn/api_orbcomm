from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base


class Rol(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)

    # Referencias foreign keys -> hijos
    rol_permiso = relationship("RolPermiso", back_populates="rol")
    usuario_rol  = relationship("UsuarioRol", back_populates="rol")