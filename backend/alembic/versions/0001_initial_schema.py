"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-02 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('subdominio', sa.String(), nullable=False),
        sa.Column('nombre_negocio', sa.String(), nullable=False),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('color_marca', sa.String(), nullable=True),
        sa.Column('activo', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('plan_suscripcion', sa.String(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(op.f('ix_tenants_id'), 'tenants', ['id'], unique=False)
    op.create_index(op.f('ix_tenants_subdominio'), 'tenants', ['subdominio'], unique=True)

    # 2. Sucursales
    op.create_table(
        'sucursales',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('direccion', sa.String(), nullable=True),
        sa.Column('telefono', sa.String(), nullable=True),
        sa.Column('activa', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(op.f('ix_sucursales_id'), 'sucursales', ['id'], unique=False)

    # 3. Precios Config
    op.create_table(
        'precios_config',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('sucursal_id', sa.Integer(), sa.ForeignKey('sucursales.id'), nullable=True),
        sa.Column('precio_bn_pagina', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('precio_color_pagina', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('recargo_a3', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('recargo_oficio', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('descuento_doble_faz', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(op.f('ix_precios_config_id'), 'precios_config', ['id'], unique=False)

    # 4. Usuarios
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('apellido', sa.String(), server_default='', nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('telefono', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('email_verificado', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('activo', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('rol', sa.String(), server_default='cliente', nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.UniqueConstraint('tenant_id', 'email', name='uq_usuarios_tenant_email'),
    )
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=False)

    # 5. Tenant Contadores
    op.create_table(
        'tenant_contadores',
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), primary_key=True, nullable=False),
        sa.Column('ultimo_codigo', sa.Integer(), server_default='0', nullable=False),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # 6. Pedidos
    op.create_table(
        'pedidos',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('sucursal_id', sa.Integer(), sa.ForeignKey('sucursales.id'), nullable=False),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('codigo', sa.String(length=32), nullable=False),
        sa.Column('contacto_invitado_nombre', sa.String(), nullable=True),
        sa.Column('contacto_invitado_mail_o_tel', sa.String(), nullable=True),
        sa.Column('token_seguimiento', sa.String(), nullable=True),
        sa.Column('descripcion_trabajo', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(), server_default='recibido', nullable=False),
        sa.Column('cantidad_copias', sa.Integer(), server_default='1', nullable=False),
        sa.Column('rango_paginas', sa.String(), nullable=True),
        sa.Column('color', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('tamano_papel', sa.String(), server_default='A4', nullable=False),
        sa.Column('doble_faz', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('precio_estimado', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('nota_interna', sa.Text(), nullable=True),
        sa.Column('operador_asignado', sa.String(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('expira_en', sa.DateTime(timezone=True), nullable=True),
        sa.Column('impreso_en', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('tenant_id', 'codigo', name='uq_pedidos_tenant_codigo'),
    )
    op.create_index(op.f('ix_pedidos_id'), 'pedidos', ['id'], unique=False)
    op.create_index(op.f('ix_pedidos_codigo'), 'pedidos', ['codigo'], unique=False)
    op.create_index(op.f('ix_pedidos_token_seguimiento'), 'pedidos', ['token_seguimiento'], unique=True)

    # 7. Archivos
    op.create_table(
        'archivos',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('pedido_id', sa.Integer(), sa.ForeignKey('pedidos.id'), nullable=False),
        sa.Column('path_storage', sa.String(), nullable=False),
        sa.Column('nombre_original', sa.String(), nullable=False),
        sa.Column('tamano_bytes', sa.Integer(), nullable=False),
        sa.Column('cantidad_paginas_detectada', sa.Integer(), nullable=True),
        sa.Column('subido_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(op.f('ix_archivos_id'), 'archivos', ['id'], unique=False)

    # 8. Sesiones Verificación
    op.create_table(
        'sesiones_verificacion',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('tipo', sa.String(), server_default='registro_mail', nullable=False),
        sa.Column('contacto', sa.String(), nullable=True),
        sa.Column('usado', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('expira_en', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_sesiones_verificacion_id'), 'sesiones_verificacion', ['id'], unique=False)
    op.create_index(op.f('ix_sesiones_verificacion_token'), 'sesiones_verificacion', ['token'], unique=True)

    # 9. Suscripciones
    op.create_table(
        'suscripciones',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('plan', sa.String(), nullable=False),
        sa.Column('precio_mensual', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('estado', sa.String(), server_default='activa', nullable=True),
        sa.Column('fecha_inicio', sa.DateTime(timezone=True), nullable=False),
        sa.Column('proximo_vencimiento', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_suscripciones_id'), 'suscripciones', ['id'], unique=False)

def downgrade() -> None:
    op.drop_table('suscripciones')
    op.drop_table('sesiones_verificacion')
    op.drop_table('archivos')
    op.drop_table('pedidos')
    op.drop_table('tenant_contadores')
    op.drop_table('usuarios')
    op.drop_table('precios_config')
    op.drop_table('sucursales')
    op.drop_table('tenants')

