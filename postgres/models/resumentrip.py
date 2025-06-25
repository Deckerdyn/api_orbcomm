from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ResumenTrip(Base):
    __tablename__ = "resumen_trip"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    id_resumen = Column(Integer, primary_key=True, index=True)

    fecha_salida_real = Column(DateTime)
    fecha_llegada_real = Column(DateTime)
    latitud_inicio = Column(Float)
    longitud_inicio = Column(Float)
    latitud_fin = Column(Float)
    longitud_fin = Column(Float)
    duracion_min = Column(Integer)
    velocidad_promedio = Column(Float)

    id_trip = Column(Integer, ForeignKey("public.trips.id_trip"))

    # Referencias a padres
    trip = relationship("Trip", back_populates="resumen_trip", lazy="joined")