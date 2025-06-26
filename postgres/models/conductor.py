from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class EstadoEnum(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class Conductor(Base):
    __tablename__ = "conductores"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    id_conductor = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("public.empresas.id_empresa"))
    id_usuario = Column(Integer, ForeignKey("public.usuarios.id_usuario"))

    licencia_numero = Column(String)
    fecha_expiracion = Column(Date)
    telefono_contacto = Column(String)
    fecha_contratacion = Column(Date)
    estado = Column(Enum(EstadoEnum))

    # Referencias a padres
    usuario = relationship("Usuario", back_populates="conductores", lazy="joined")
    empresa = relationship("Empresa", back_populates="conductores", lazy="joined")

    # Referencias foreign keys -> hijos
    trip_conductores = relationship("TripConductor", back_populates="conductor")
    vehiculo_conductor = relationship("VehiculoConductor", back_populates="conductor")
