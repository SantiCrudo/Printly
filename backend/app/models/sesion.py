from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class SesionVerificacion(Base):
    __tablename__ = "sesiones_verificacion"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    token = Column(String, unique=True, index=True, nullable=False)
    tipo = Column(String, default="registro_mail", nullable=False) # registro_mail | login_magic_link
    contacto = Column(String, nullable=True)
    usado = Column(Boolean, default=False, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    expira_en = Column(DateTime(timezone=True), nullable=False)
