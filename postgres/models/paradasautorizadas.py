from sqlalchemy import Column, Integer, String, Enum
from geoalchemy2 import Geometry
from sqlalchemy.orm import declarative_base, relationship
from ..database import Base
import enum

class EstadoEnum(enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class ParadasAutorizadas(Base):
    __tablename__ = "paradas_autorizadas"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_parada = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    geom = Column(Geometry, nullable=True)
    estado = Column(Enum(EstadoEnum), default=EstadoEnum.activo)

    # Referencias foreign keys -> hijos
    ruta_parada = relationship("RutaParada", back_populates="parada")