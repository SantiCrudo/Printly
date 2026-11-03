from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.sql import func
from app.models.base import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    codigo = Column(String(32), nullable=False, index=True)
    contacto_invitado_nombre = Column(String, nullable=True)
    contacto_invitado_mail_o_tel = Column(String, nullable=True)
    token_seguimiento = Column(String, unique=True, index=True, nullable=True)
    descripcion_trabajo = Column(Text, nullable=True)
    estado = Column(String, default="recibido", nullable=False) # recibido, en_cola, imprimiendo, listo, entregado, expirado, cancelado
    cantidad_copias = Column(Integer, default=1, nullable=False)
    rango_paginas = Column(String, nullable=True)
    color = Column(Boolean, default=False, nullable=False)
    tamano_papel = Column(String, default="A4", nullable=False)
    doble_faz = Column(Boolean, default=False, nullable=False)
    precio_estimado = Column(Numeric(10, 2), nullable=True)
    nota_interna = Column(Text, nullable=True)
    operador_asignado = Column(String, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    expira_en = Column(DateTime(timezone=True), nullable=True)
    impreso_en = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "codigo", name="uq_pedidos_tenant_codigo"),
    )
