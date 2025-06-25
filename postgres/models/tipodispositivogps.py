from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class TipoDispositivoGPS(Base):
    __tablename__ = "tipodispositivogps"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    id_tipodispositivo = Column(Integer,primary_key=True, index=True)
    nombre = Column(String, nullable=False);

    # Referencias a hijos
    dispositivo_gps = relationship("DispositivoGPS", back_populates="tipo_dispositivo")