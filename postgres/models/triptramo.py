from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class TripTramo(Base):
    __tablename__ = "trip_tramos"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    orden = Column(Integer)
    fecha_salida = Column(DateTime)
    fecha_llegada = Column(DateTime)

    id_trip = Column(Integer, ForeignKey("public.trips.id_trip"), primary_key=True)
    id_tramo = Column(Integer, ForeignKey("public.tramos.id_tramo"), primary_key=True)
    id_estado = Column(Integer, ForeignKey("public.estados_viaje.id_estado"))

    # Referencias a padres
    trip = relationship("Trip", back_populates="trip_tramo", lazy="joined")
    tramo = relationship("Tramo", back_populates="trip_tramo", lazy="joined")
    estado = relationship("EstadoViaje", back_populates="trip_tramo", lazy="joined")