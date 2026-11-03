from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class Archivo(Base):
    __tablename__ = "archivos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    path_storage = Column(String, nullable=False)
    nombre_original = Column(String, nullable=False)
    tamano_bytes = Column(Integer, nullable=False)
    cantidad_paginas_detectada = Column(Integer, nullable=True)
    subido_en = Column(DateTime(timezone=True), server_default=func.now())
