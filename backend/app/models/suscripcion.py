from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from app.models.base import Base

class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    plan = Column(String, nullable=False)
    precio_mensual = Column(Numeric(10, 2), nullable=False)
    estado = Column(String, default="activa") # activa, vencida, cancelada
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    proximo_vencimiento = Column(DateTime(timezone=True), nullable=False)
