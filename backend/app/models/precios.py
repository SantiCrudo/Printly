from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class PreciosConfig(Base):
    __tablename__ = "precios_config"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    precio_bn_pagina = Column(Numeric(10, 2), nullable=False)
    precio_color_pagina = Column(Numeric(10, 2), nullable=False)
    recargo_a3 = Column(Numeric(10, 2), nullable=True)
    recargo_oficio = Column(Numeric(10, 2), nullable=True)
    descuento_doble_faz = Column(Numeric(10, 2), nullable=True)
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
