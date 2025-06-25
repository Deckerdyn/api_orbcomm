from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class VehiculoConductor(Base):
    __tablename__ = "vehiculo_conductores"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

    id_vehiculo = Column(Integer, ForeignKey("public.vehiculos.id_vehiculo"), primary_key=True)
    id_conductor = Column(Integer, ForeignKey("public.conductores.id_conductor"), primary_key=True)

    # Referencias a padres
    vehiculo = relationship("Vehiculo", back_populates="vehiculo_conductor", lazy="joined")
    conductor = relationship("Conductor", back_populates="vehiculo_conductor", lazy="joined")