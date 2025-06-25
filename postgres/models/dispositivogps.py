from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class EstadoEnum(enum.Enum):
    activo = "activo"
    inactivo = "inactivo"

class DispositivoGPS(Base):
    __tablename__ = "dispositivo_gps"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    id_dispositivo = Column(Integer, primary_key=True, index=True, autoincrement=True)

    proveedor = Column(String)
    numero_serie = Column(String)
    fecha_instalacion = Column(Date)
    estado = Column(String)
    
    id_tipodispositivo = Column(Integer, ForeignKey("public.tipodispositivogps.id_tipodispositivo"))

    # Referencias a padres
    tipo_dispositivo = relationship("TipoDispositivoGPS", back_populates="dispositivo_gps", lazy="joined")

    # Referencias foreign keys -> hijos
    vehiculos = relationship("Vehiculo", back_populates="dispositivo")
    
