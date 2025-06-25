from sqlalchemy import Column, Integer, String, Enum , ForeignKey, Float
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class EstadoEnum(enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class Tramo(Base):
    __tablename__ = "tramos"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_tramo = Column(Integer, primary_key=True, index=True)
    distancia_km = Column(Float, nullable=False)
    tiempo_estimado_min = Column(Integer, nullable=False)
    descripcion = Column(String, nullable=True)
    estado = Column(Enum(EstadoEnum), default=EstadoEnum.activo)

    id_origen = Column(Integer, ForeignKey("public.ubicaciones.id_ubicacion"))
    id_destino = Column(Integer ,ForeignKey("public.ubicaciones.id_ubicacion"))
    
    #Referencia a padres
    origen = relationship("Ubicacion", foreign_keys=[id_origen], back_populates="tramos_origen", lazy="joined")
    destino = relationship("Ubicacion", foreign_keys=[id_destino], back_populates="tramos_destino", lazy="joined")

    # Referencias foreign keys -> hijos
    ruta_tramo = relationship("RutaTramo", back_populates="tramo")
    trip_tramo = relationship("TripTramo", back_populates="tramo")