from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class RutaParada(Base):
    __tablename__ = "ruta_paradas"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas

    orden = Column(Integer)

    id_ruta = Column(Integer, ForeignKey("public.rutas.id_ruta"), primary_key=True)
    id_parada = Column(Integer, ForeignKey("public.paradas_autorizadas.id_parada"), primary_key=True)

    # Referencias a padres
    ruta = relationship("Ruta", back_populates="ruta_parada", lazy="joined")
    parada = relationship("ParadasAutorizadas", back_populates="ruta_parada", lazy="joined")