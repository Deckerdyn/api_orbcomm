from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base

class TripLog(Base):
    __tablename__ = "trip_logs"
    __table_args__ = {"schema": "public"}

    id_log = Column(Integer, primary_key=True, index=True)
    
    id_trip = Column(JSONB, nullable=False, default=None)
    accion = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    origen = Column(String, default="sistema")

    usuario_id = Column(JSONB, nullable=False, default=None)
    id_vehiculo = Column(JSONB, nullable=False, default=None)
    id_conductor = Column(JSONB, nullable=False, default=None)
    id_empresa = Column(JSONB, nullable=False, default=None)
    id_ruta = Column(JSONB, nullable=False, default=None)
    patente_vehiculo = Column(String, nullable=False)
    nombre_conductor = Column(String, nullable=False)
    rut_empresa = Column(String, nullable=False)
    origen_viaje = Column(String, nullable=False)
    destino_viaje = Column(String, nullable=False)
    fecha_log = Column(DateTime(timezone=True), server_default=func.now())
    fecha_salida_prog = Column(DateTime(timezone=True), nullable=False)
    fecha_llegada_estim = Column(DateTime(timezone=True), nullable=False)
    comentarios = Column(String, nullable=True)

    # Referencias a padres
    # trip = relationship("Trip", back_populates="logs", lazy="joined")
    
    # Referencias foreign keys -> hijos
    # usuario = relationship("Usuario", lazy="joined")
    # vehiculo = relationship("Vehiculo", lazy="joined")
    # conductor = relationship("Conductor", lazy="joined")
    # empresa = relationship("Empresa", lazy="joined")
    # ruta = relationship("Ruta", lazy="joined")