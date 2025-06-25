from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class RolPermiso(Base):
    __tablename__ = "rol_permiso"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_rol = Column(Integer, ForeignKey("public.roles.id_rol"), primary_key=True)
    id_permiso = Column(Integer, ForeignKey("public.permisos.id_permiso"), primary_key=True)

    # Referencias a padres
    rol = relationship("Rol", back_populates="rol_permiso", lazy="joined")
    permiso = relationship("Permiso", back_populates="rol_permiso", lazy="joined")