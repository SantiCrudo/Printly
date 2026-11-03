from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.models.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False, default="")
    email = Column(String, nullable=False, index=True)
    telefono = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    email_verificado = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    rol = Column(String, default="cliente", nullable=False) # cliente | operador | admin
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_usuarios_tenant_email"),
    )
