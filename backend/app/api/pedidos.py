import os
import shutil
import uuid
import secrets
import aiofiles
import httpx
from decimal import Decimal
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.config import settings
from app.api.dependencies import (
    get_current_tenant, 
    get_current_active_user, 
    require_operador_o_admin
)
from app.models.pedido import Pedido
from app.models.archivo import Archivo
from app.models.tenant import Tenant
from app.models.sucursal import Sucursal
from app.models.precios import PreciosConfig
from app.models.usuario import Usuario
from app.services.pricing import calcular_precio_con_config
from app.services.counter import generar_codigo_pedido
from app.core.email import send_status_update_email

router = APIRouter()

async def procesar_archivo_upload(archivo: UploadFile) -> tuple[str, str, int]:
    os.makedirs("storage", exist_ok=True)
    file_ext = os.path.splitext(archivo.filename)[1]
    file_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join("storage", file_name)
    
    content = await archivo.read()
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(content)
        
    return file_path, archivo.filename, len(content)

async def validar_turnstile(token: str):
    if settings.ENVIRONMENT == "production":
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify", 
                data={
                    "secret": settings.TURNSTILE_SECRET_KEY,
                    "response": token
                }
            )
            if not r.json().get("success"):
                raise HTTPException(status_code=400, detail="Validación anti-bot fallida")
    else:
        # En desarrollo / test, si viene token de prueba de Cloudflare o dummy se permite
        if not token:
            raise HTTPException(status_code=400, detail="Token anti-bot requerido")

@router.post("/invitado")
async def crear_pedido_invitado(
    nombre: str = Form(...),
    contacto: str = Form(""),
    desc: str = Form(""),
    copias: int = Form(1),
    paginas: int = Form(1),
    color: bool = Form(False),
    doble_faz: bool = Form(False),
    tamano: str = Form("A4"),
    sucursal_id: int = Form(...),
    turnstile_token: str = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    await validar_turnstile(turnstile_token)

    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id, Sucursal.tenant_id == tenant.id).first()
    if not sucursal:
        raise HTTPException(status_code=400, detail="Sucursal inválida")

    precios_config = db.query(PreciosConfig).filter(PreciosConfig.tenant_id == tenant.id).first()
    precio = calcular_precio_con_config(
        precios_config=precios_config,
        color=color,
        tamano=tamano,
        paginas=paginas,
        copias=copias,
        doble_faz=doble_faz
    )

    codigo = generar_codigo_pedido(db, tenant.id)
    token = secrets.token_urlsafe(12)

    file_path, original_name, size = await procesar_archivo_upload(archivo)

    nuevo_pedido = Pedido(
        tenant_id=tenant.id,
        sucursal_id=sucursal.id,
        codigo=codigo,
        contacto_invitado_nombre=nombre.strip(),
        contacto_invitado_mail_o_tel=contacto.strip(),
        token_seguimiento=token,
        descripcion_trabajo=desc,
        estado="recibido",
        cantidad_copias=copias,
        rango_paginas=str(paginas),
        color=color,
        tamano_papel=tamano,
        doble_faz=doble_faz,
        precio_estimado=precio
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    db.add(Archivo(
        pedido_id=nuevo_pedido.id,
        path_storage=file_path,
        nombre_original=original_name,
        tamano_bytes=size
    ))
    db.commit()

    return {
        "id": nuevo_pedido.id, 
        "codigo": nuevo_pedido.codigo, 
        "token_seguimiento": token, 
        "precio_estimado": float(precio)
    }

@router.post("/registrado")
async def crear_pedido_registrado(
    desc: str = Form(""),
    copias: int = Form(1),
    paginas: int = Form(1),
    color: bool = Form(False),
    doble_faz: bool = Form(False),
    tamano: str = Form("A4"),
    sucursal_id: int = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    user: Usuario = Depends(get_current_active_user)
):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id, Sucursal.tenant_id == tenant.id).first()
    if not sucursal:
        raise HTTPException(status_code=400, detail="Sucursal inválida")

    precios_config = db.query(PreciosConfig).filter(PreciosConfig.tenant_id == tenant.id).first()
    precio = calcular_precio_con_config(
        precios_config=precios_config,
        color=color,
        tamano=tamano,
        paginas=paginas,
        copias=copias,
        doble_faz=doble_faz
    )

    codigo = generar_codigo_pedido(db, tenant.id)
    token = secrets.token_urlsafe(12)

    file_path, original_name, size = await procesar_archivo_upload(archivo)

    nuevo_pedido = Pedido(
        tenant_id=tenant.id,
        sucursal_id=sucursal.id,
        usuario_id=user.id,
        codigo=codigo,
        contacto_invitado_nombre=f"{user.nombre} {user.apellido}".strip(),
        token_seguimiento=token,
        descripcion_trabajo=desc,
        estado="recibido",
        cantidad_copias=copias,
        rango_paginas=str(paginas),
        color=color,
        tamano_papel=tamano,
        doble_faz=doble_faz,
        precio_estimado=precio
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    db.add(Archivo(
        pedido_id=nuevo_pedido.id,
        path_storage=file_path,
        nombre_original=original_name,
        tamano_bytes=size
    ))
    db.commit()

    return {
        "id": nuevo_pedido.id, 
        "codigo": nuevo_pedido.codigo, 
        "token_seguimiento": token, 
        "precio_estimado": float(precio)
    }

@router.post("/{pedido_id}/repetir")
def repetir_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    user: Usuario = Depends(get_current_active_user)
):
    pedido_viejo = db.query(Pedido).filter(
        Pedido.id == pedido_id, 
        Pedido.usuario_id == user.id, 
        Pedido.tenant_id == tenant.id
    ).first()
    if not pedido_viejo:
        raise HTTPException(status_code=404, detail="Pedido original no encontrado")
    
    archivo_viejo = db.query(Archivo).filter(Archivo.pedido_id == pedido_viejo.id).first()
    if not archivo_viejo:
        raise HTTPException(status_code=404, detail="Archivo original no encontrado")

    codigo = generar_codigo_pedido(db, tenant.id)
    token = secrets.token_urlsafe(12)

    precios_config = db.query(PreciosConfig).filter(PreciosConfig.tenant_id == tenant.id).first()
    paginas = int(pedido_viejo.rango_paginas) if (pedido_viejo.rango_paginas and pedido_viejo.rango_paginas.isdigit()) else 1
    precio = calcular_precio_con_config(
        precios_config=precios_config,
        color=pedido_viejo.color,
        tamano=pedido_viejo.tamano_papel,
        paginas=paginas,
        copias=pedido_viejo.cantidad_copias,
        doble_faz=pedido_viejo.doble_faz
    )

    nuevo_pedido = Pedido(
        tenant_id=tenant.id,
        sucursal_id=pedido_viejo.sucursal_id,
        usuario_id=user.id,
        codigo=codigo,
        contacto_invitado_nombre=f"{user.nombre} {user.apellido}".strip(),
        token_seguimiento=token,
        descripcion_trabajo=f"{pedido_viejo.descripcion_trabajo or ''} (Reimpresión)".strip(),
        estado="recibido",
        cantidad_copias=pedido_viejo.cantidad_copias,
        rango_paginas=pedido_viejo.rango_paginas,
        color=pedido_viejo.color,
        tamano_papel=pedido_viejo.tamano_papel,
        doble_faz=pedido_viejo.doble_faz,
        precio_estimado=precio
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    # Duplicar el archivo físico para que el borrado independiente no lo rompa
    orig_path = archivo_viejo.path_storage
    if os.path.exists(orig_path):
        ext = os.path.splitext(orig_path)[1]
        nuevo_file_name = f"{uuid.uuid4().hex}{ext}"
        nuevo_path = os.path.join("storage", nuevo_file_name)
        shutil.copy2(orig_path, nuevo_path)
    else:
        nuevo_path = orig_path

    db.add(Archivo(
        pedido_id=nuevo_pedido.id,
        path_storage=nuevo_path,
        nombre_original=archivo_viejo.nombre_original,
        tamano_bytes=archivo_viejo.tamano_bytes
    ))
    db.commit()

    return {
        "id": nuevo_pedido.id, 
        "codigo": nuevo_pedido.codigo, 
        "token_seguimiento": token,
        "precio_estimado": float(precio)
    }

@router.get("/mis-pedidos")
def mis_pedidos(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    user: Usuario = Depends(get_current_active_user)
):
    pedidos = db.query(Pedido).filter(
        Pedido.usuario_id == user.id, 
        Pedido.tenant_id == tenant.id
    ).order_by(desc(Pedido.creado_en)).all()
    resultado = []
    for p in pedidos:
        archivo = db.query(Archivo).filter(Archivo.pedido_id == p.id).first()
        resultado.append({
            "id": p.id,
            "codigo": p.codigo,
            "token": p.token_seguimiento,
            "desc": p.descripcion_trabajo,
            "copias": p.cantidad_copias,
            "paginas": p.rango_paginas,
            "color": p.color,
            "tamano": p.tamano_papel,
            "dobleFaz": p.doble_faz,
            "precio": float(p.precio_estimado) if p.precio_estimado is not None else 0.0,
            "estado": p.estado,
            "creado": p.creado_en.isoformat() if p.creado_en else None,
            "fileName": archivo.nombre_original if archivo else "Sin archivo"
        })
    return resultado

@router.get("/seguimiento/{token}")
def seguimiento_pedido(
    token: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Pantalla pública de solo lectura: código, estado con stepper, sucursal, precio, hora de creación.
    NO expone el archivo ni datos sensibles personales.
    """
    pedido = db.query(Pedido).filter(
        Pedido.token_seguimiento == token,
        Pedido.tenant_id == tenant.id
    ).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado con este token")

    sucursal = db.query(Sucursal).filter(Sucursal.id == pedido.sucursal_id).first()

    return {
        "codigo": pedido.codigo,
        "estado": pedido.estado,
        "sucursal_nombre": sucursal.nombre if sucursal else "Casa Central",
        "sucursal_direccion": sucursal.direccion if sucursal else None,
        "precio_estimado": float(pedido.precio_estimado) if pedido.precio_estimado is not None else 0.0,
        "creado_en": pedido.creado_en.isoformat() if pedido.creado_en else None,
        "cantidad_copias": pedido.cantidad_copias,
        "color": pedido.color,
        "tamano_papel": pedido.tamano_papel,
        "doble_faz": pedido.doble_faz
    }

@router.get("/")
def listar_pedidos(
    db: Session = Depends(get_db), 
    tenant: Tenant = Depends(get_current_tenant),
    operador: Usuario = Depends(require_operador_o_admin)
):
    pedidos = db.query(Pedido).filter(Pedido.tenant_id == tenant.id).order_by(desc(Pedido.creado_en)).all()
    resultado = []
    for p in pedidos:
        archivo = db.query(Archivo).filter(Archivo.pedido_id == p.id).first()
        sucursal = db.query(Sucursal).filter(Sucursal.id == p.sucursal_id).first()
        resultado.append({
            "id": p.id,
            "codigo": p.codigo,
            "token": p.token_seguimiento,
            "nombre": p.contacto_invitado_nombre or "Usuario registrado",
            "tipo": "invitado" if p.usuario_id is None else "registrado",
            "desc": p.descripcion_trabajo,
            "copias": p.cantidad_copias,
            "paginas": p.rango_paginas,
            "color": p.color,
            "tamano": p.tamano_papel,
            "dobleFaz": p.doble_faz,
            "precio": float(p.precio_estimado) if p.precio_estimado is not None else 0.0,
            "estado": p.estado,
            "creado": p.creado_en.isoformat() if p.creado_en else None,
            "fileName": archivo.nombre_original if archivo else "Sin archivo",
            "fileId": archivo.id if archivo else None,
            "sucursal_id": p.sucursal_id,
            "sucursal_nombre": sucursal.nombre if sucursal else "Desconocida"
        })
    return resultado

class EstadoUpdate(BaseModel):
    estado: str

@router.patch("/{pedido_id}/estado")
def actualizar_estado(
    pedido_id: int, 
    payload: EstadoUpdate, 
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    operador: Usuario = Depends(require_operador_o_admin)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id, Pedido.tenant_id == tenant.id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    pedido.estado = payload.estado
    db.commit()
    
    if pedido.usuario_id:
        usuario = db.query(Usuario).filter(Usuario.id == pedido.usuario_id).first()
        if usuario:
            send_status_update_email(usuario.email, usuario.nombre, pedido.codigo, pedido.estado, tenant.subdominio)
            
    return {"message": "Estado actualizado", "nuevo_estado": pedido.estado}
