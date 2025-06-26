from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class UsuarioRol(Base):
    __tablename__ = "usuario_rol"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_usuario = Column(Integer, ForeignKey("public.usuarios.id_usuario"), primary_key=True)
    id_rol = Column(Integer, ForeignKey("public.roles.id_rol"), primary_key=True)

    # Referencias a padres
    usuario = relationship("Usuario", back_populates="usuario_rol", lazy="joined")
    rol = relationship("Rol", back_populates="usuario_rol", lazy="joined")