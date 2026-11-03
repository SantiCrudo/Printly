from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class TenantContador(Base):
    __tablename__ = "tenant_contadores"

    tenant_id = Column(Integer, ForeignKey("tenants.id"), primary_key=True)
    ultimo_codigo = Column(Integer, default=0, nullable=False)
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

