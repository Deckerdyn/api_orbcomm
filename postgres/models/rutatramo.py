from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class RutaTramo(Base):
    __tablename__ = "ruta_tramos"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    orden = Column(Integer)
    
    id_ruta = Column(Integer, ForeignKey("public.rutas.id_ruta"), primary_key=True)
    id_tramo = Column(Integer, ForeignKey("public.tramos.id_tramo"), primary_key=True)

    # Referencias a padres
    ruta = relationship("Ruta", back_populates="ruta_tramo", lazy="joined")
    tramo = relationship("Tramo", back_populates="ruta_tramo", lazy="joined")