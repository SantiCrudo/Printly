from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_tenant, require_operador_o_admin
from app.models.pedido import Pedido
from app.models.tenant import Tenant
from app.models.sucursal import Sucursal
from app.models.usuario import Usuario

router = APIRouter()

ESTADOS_CONOCIDOS = ["recibido", "en_cola", "imprimiendo", "listo", "entregado", "expirado", "cancelado"]

@router.get("/")
def get_stats(
    periodo: str = "hoy", # hoy, semana, mes, todos
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    operador: Usuario = Depends(require_operador_o_admin)
):
    query = db.query(Pedido).filter(Pedido.tenant_id == tenant.id)
    
    now = datetime.utcnow()
    if periodo == "hoy":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == "semana":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == "mes":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = None

    if start_date:
        query = query.filter(Pedido.creado_en >= start_date)

    pedidos = query.all()

    por_estado = {estado: 0 for estado in ESTADOS_CONOCIDOS}
    por_sucursal = {}

    sucursales = db.query(Sucursal).filter(Sucursal.tenant_id == tenant.id).all()
    for s in sucursales:
        por_sucursal[s.nombre] = {
            "pedidos": 0, 
            "facturacion_estimada": Decimal("0.00"),
            "facturacion_cobrada": Decimal("0.00")
        }

    total_archivos_impresos = 0
    pendientes = 0
    paginas_bn = 0
    paginas_color = 0
    facturacion_estimada = Decimal("0.00")
    facturacion_cobrada = Decimal("0.00")

    for p in pedidos:
        # Paginación
        try:
            pags_unitarias = int(p.rango_paginas) if (p.rango_paginas and p.rango_paginas.isdigit()) else 1
        except (ValueError, TypeError):
            pags_unitarias = 1
            
        total_pags_pedido = pags_unitarias * (p.cantidad_copias or 1)
        if p.color:
            paginas_color += total_pags_pedido
        else:
            paginas_bn += total_pags_pedido

        # Contabilizar estado de forma segura sin KeyError
        estado_norm = p.estado.lower() if p.estado else "recibido"
        if estado_norm in por_estado:
            por_estado[estado_norm] += 1
        else:
            por_estado[estado_norm] = 1

        precio_p = Decimal(str(p.precio_estimado)) if p.precio_estimado is not None else Decimal("0.00")

        # Separar facturación estimada (no cancelados ni expirados) y facturación cobrada (entregados)
        if estado_norm not in ("cancelado", "expirado"):
            facturacion_estimada += precio_p

        if estado_norm == "entregado":
            facturacion_cobrada += precio_p
            total_archivos_impresos += 1
        elif estado_norm == "listo":
            total_archivos_impresos += 1
        elif estado_norm not in ("cancelado", "expirado"):
            pendientes += 1

        # Sucursal
        s_nombre = next((s.nombre for s in sucursales if s.id == p.sucursal_id), "Desconocida")
        if s_nombre not in por_sucursal:
            por_sucursal[s_nombre] = {
                "pedidos": 0, 
                "facturacion_estimada": Decimal("0.00"),
                "facturacion_cobrada": Decimal("0.00")
            }
        por_sucursal[s_nombre]["pedidos"] += 1
        if estado_norm not in ("cancelado", "expirado"):
            por_sucursal[s_nombre]["facturacion_estimada"] += precio_p
        if estado_norm == "entregado":
            por_sucursal[s_nombre]["facturacion_cobrada"] += precio_p

    chart_estados = [{"name": k.replace("_", " ").title(), "value": v} for k, v in por_estado.items() if v > 0]
    chart_sucursales = [
        {"name": k, "facturacion": float(v["facturacion_estimada"]), "cobrada": float(v["facturacion_cobrada"])} 
        for k, v in por_sucursal.items()
    ]
    
    return {
        "kpis": {
            "impresos": total_archivos_impresos,
            "pendientes": pendientes,
            "facturacion": float(facturacion_estimada),
            "facturacion_estimada": float(facturacion_estimada),
            "facturacion_cobrada": float(facturacion_cobrada),
            "paginas_bn": paginas_bn,
            "paginas_color": paginas_color
        },
        "charts": {
            "estados": chart_estados,
            "sucursales": chart_sucursales
        }
    }
