from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import  relationship
from ..database import Base


class Permiso(Base):
    __tablename__ = "permisos"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_permiso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Referencias foreign keys -> hijos
    rol_permiso = relationship("RolPermiso", back_populates="permiso")