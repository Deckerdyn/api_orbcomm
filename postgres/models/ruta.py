from sqlalchemy import Column, Integer, String, Enum , ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class EstadoEnum(enum.Enum):
    activo = "activo"    
    inactivo = "inactivo"

class Ruta(Base):
    __tablename__ = "rutas"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_ruta = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(String, default="activo")

    id_origen = Column(Integer, ForeignKey("public.ubicaciones.id_ubicacion"))
    id_destino = Column(Integer ,ForeignKey("public.ubicaciones.id_ubicacion"))
    
    #Referencia a padres
    origen = relationship("Ubicacion", foreign_keys=[id_origen], back_populates="rutas_origen", lazy="joined")
    destino = relationship("Ubicacion", foreign_keys=[id_destino], back_populates="rutas_destino", lazy="joined")

    # Referencias foreign keys -> hijos
    trips = relationship("Trip", back_populates="ruta")
    ruta_tramo = relationship("RutaTramo", back_populates="ruta")
    ruta_parada = relationship("RutaParada", back_populates="ruta")
    