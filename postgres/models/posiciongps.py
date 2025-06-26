from sqlalchemy import Column, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class PosicionGPS(Base):
    __tablename__ = "posicion_gps"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    id_registro = Column(Integer, primary_key=True, index=True)

    timestamp = Column(Date)
    latitud = Column(Float)
    longitud = Column(Float)
    velocidad_kmh = Column(Float)
    rumbo_grados = Column(Float)

    id_trip = Column(Integer, ForeignKey("public.trips.id_trip"))

    # Referencias a padres
    trip = relationship("Trip", back_populates="posicion_gps", lazy="joined")