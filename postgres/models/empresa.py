from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from ..database import Base
import enum
from datetime import datetime

class EstadoEnum(enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class Empresa(Base):
    __tablename__ = "empresas"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_empresa = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    rut = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    telefono_contacto = Column(String, nullable=True)
    email = Column(String, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    estado = Column(String, default="activo")
    
    # Referencias foreign keys -> hijos
    conductores = relationship("Conductor", back_populates="empresa")
    vehiculos = relationship("Vehiculo", back_populates="empresa") 
    trips = relationship("Trip", back_populates="empresa")
