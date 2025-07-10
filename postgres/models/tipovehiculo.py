from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base 

class TipoVehiculo(Base):
    __tablename__ = "tipo_vehiculos"
    __table_args__ = {"schema": "public"}

    id_tipo_vehiculo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)

    vehiculos = relationship("Vehiculo", back_populates="tipo_vehiculo")