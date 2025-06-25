from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class EstadoEnum(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    id_vehiculo = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("public.empresas.id_empresa"))
    id_dispositivo = Column(Integer, ForeignKey("public.dispositivo_gps.id_dispositivo"))

    placa = Column(String)
    modelo = Column(String)
    anio = Column(Integer)
    capacidad_kg = Column(Integer)
    estado = Column(Enum(EstadoEnum))

    # Referencias a padres
    empresa = relationship("Empresa", back_populates="vehiculos", lazy="joined")
    dispositivo = relationship("DispositivoGPS", back_populates="vehiculos", lazy="joined")

    # Referencias foreign keys -> hijos
    trips = relationship("Trip", back_populates="vehiculo")
    vehiculo_conductor = relationship("VehiculoConductor", back_populates="vehiculo")