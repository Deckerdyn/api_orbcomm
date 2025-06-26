from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime


class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = {"schema": "public"}  # ubicacion de las tablas
    
    id_trip = Column(Integer, primary_key=True, index=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    fecha_salida_prog = Column(DateTime, nullable=True)
    fecha_llegada_estim = Column(DateTime, nullable=True)
    fecha_salida_real = Column(DateTime, nullable=True)
    fecha_llegada_real = Column(DateTime, nullable=True)
    comentarios = Column(Text, nullable=True)

    id_ruta = Column(Integer, ForeignKey("public.rutas.id_ruta"))
    id_empresa = Column(Integer, ForeignKey("public.empresas.id_empresa"))
    id_vehiculo = Column(Integer, ForeignKey("public.vehiculos.id_vehiculo"))
    id_estado = Column(Integer, ForeignKey("public.estados_viaje.id_estado"))
    
    #Referencia a padres
    ruta = relationship("Ruta", back_populates="trips", lazy="joined")
    empresa = relationship("Empresa", back_populates="trips", lazy="joined")
    vehiculo = relationship("Vehiculo", back_populates="trips", lazy="joined")
    estado = relationship("EstadoViaje", back_populates="trips", lazy="joined")

    # Referencias foreign keys -> hijos
    posicion_gps = relationship("PosicionGPS", back_populates="trip")
    resumen_trip = relationship("ResumenTrip", back_populates="trip")
    trip_tramo = relationship("TripTramo", back_populates="trip")
    trip_conductores = relationship("TripConductor", back_populates="trip")