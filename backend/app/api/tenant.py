from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_tenant, require_operador_o_admin
from app.models.tenant import Tenant
from app.models.sucursal import Sucursal
from app.models.precios import PreciosConfig
from app.models.usuario import Usuario

router = APIRouter()

@router.get("/info")
def get_tenant_info(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    sucursales = db.query(Sucursal).filter(Sucursal.tenant_id == tenant.id, Sucursal.activa == True).all()
    precios = db.query(PreciosConfig).filter(PreciosConfig.tenant_id == tenant.id).first()
    
    if not precios:
        precios = {
            "precio_bn_pagina": 25.00,
            "precio_color_pagina": 60.00,
            "recargo_a3": 1.60,
            "recargo_oficio": 1.15,
            "descuento_doble_faz": 1.00
        }
    
    return {
        "id": tenant.id,
        "subdominio": tenant.subdominio,
        "nombre_negocio": tenant.nombre_negocio,
        "color_marca": tenant.color_marca,
        "sucursales": [{"id": s.id, "nombre": s.nombre, "direccion": s.direccion} for s in sucursales],
        "precios": {
            "precio_bn_pagina": float(precios.precio_bn_pagina) if hasattr(precios, 'precio_bn_pagina') else float(precios["precio_bn_pagina"]),
            "precio_color_pagina": float(precios.precio_color_pagina) if hasattr(precios, 'precio_color_pagina') else float(precios["precio_color_pagina"]),
            "recargo_a3": float(precios.recargo_a3) if hasattr(precios, 'recargo_a3') else float(precios["recargo_a3"]),
            "recargo_oficio": float(precios.recargo_oficio) if hasattr(precios, 'recargo_oficio') else float(precios["recargo_oficio"]),
            "descuento_doble_faz": float(precios.descuento_doble_faz) if hasattr(precios, 'descuento_doble_faz') else float(precios["descuento_doble_faz"])
        }
    }

class PreciosUpdateSchema(BaseModel):
    precio_bn_pagina: Optional[Decimal] = None
    precio_color_pagina: Optional[Decimal] = None
    recargo_a3: Optional[Decimal] = None
    recargo_oficio: Optional[Decimal] = None
    descuento_doble_faz: Optional[Decimal] = None

@router.put("/precios")
def actualizar_precios(
    payload: PreciosUpdateSchema,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    operador: Usuario = Depends(require_operador_o_admin)
):
    precios = db.query(PreciosConfig).filter(PreciosConfig.tenant_id == tenant.id).first()
    if not precios:
        precios = PreciosConfig(tenant_id=tenant.id)
        db.add(precios)

    if payload.precio_bn_pagina is not None:
        precios.precio_bn_pagina = payload.precio_bn_pagina
    if payload.precio_color_pagina is not None:
        precios.precio_color_pagina = payload.precio_color_pagina
    if payload.recargo_a3 is not None:
        precios.recargo_a3 = payload.recargo_a3
    if payload.recargo_oficio is not None:
        precios.recargo_oficio = payload.recargo_oficio
    if payload.descuento_doble_faz is not None:
        precios.descuento_doble_faz = payload.descuento_doble_faz

    db.commit()
    return {"message": "Precios actualizados con éxito"}
