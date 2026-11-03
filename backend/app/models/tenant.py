from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    subdominio = Column(String, unique=True, index=True, nullable=False)
    nombre_negocio = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    color_marca = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    plan_suscripcion = Column(String, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
