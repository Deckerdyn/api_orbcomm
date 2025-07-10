from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class EstadoViaje(Base):
    __tablename__ = "estados_viaje"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_estado = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)

    # Referencias foreign keys -> hijos
    trips = relationship("Trip", back_populates="estado_viaje")
    trip_tramo = relationship("TripTramo", back_populates="estado")