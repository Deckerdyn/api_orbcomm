from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class TripConductor(Base):
    __tablename__ = "trip_conductores"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    id_trip = Column(Integer, ForeignKey("public.trips.id_trip"), primary_key=True)
    id_conductor = Column(Integer, ForeignKey("public.conductores.id_conductor"), primary_key=True)

    # Referencias a padres
    trip = relationship("Trip", back_populates="trip_conductores", lazy="joined")
    conductor = relationship("Conductor", back_populates="trip_conductores", lazy="joined")