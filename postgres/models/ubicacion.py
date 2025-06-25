from sqlalchemy import Column, Integer, String, Enum, Float
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class TipoEnum(enum.Enum):
    origen = "origen"
    destino = "zona"
    servicio = "servicio"

class Ubicacion(Base):
    __tablename__ = "ubicaciones"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_ubicacion = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    latitud = Column(Float)
    longitud = Column(Float)
    tipo = Column(Enum(TipoEnum), default=TipoEnum.origen)
    

    # Referencias foreign keys -> hijos
    tramos_origen = relationship("Tramo", foreign_keys="[Tramo.id_origen]", back_populates="origen")
    tramos_destino = relationship("Tramo", foreign_keys="[Tramo.id_destino]", back_populates="destino")
    rutas_origen = relationship("Ruta", foreign_keys="[Ruta.id_origen]", back_populates="origen")
    rutas_destino = relationship("Ruta", foreign_keys="[Ruta.id_destino]", back_populates="destino")
