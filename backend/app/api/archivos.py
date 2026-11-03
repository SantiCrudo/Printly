import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.core.security import ALGORITHM
from app.api.dependencies import get_current_tenant
from app.models.tenant import Tenant
from app.models.archivo import Archivo
from app.models.pedido import Pedido
from app.models.usuario import Usuario

router = APIRouter()

@router.get("/{archivo_id}")
def obtener_archivo(
    archivo_id: int, 
    token: Optional[str] = Query(None, description="Token de seguimiento del pedido"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    archivo = db.query(Archivo).filter(Archivo.id == archivo_id).first()
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    pedido = db.query(Pedido).filter(Pedido.id == archivo.pedido_id).first()
    if not pedido or pedido.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Archivo no encontrado en este comercio")

    # Regla de acceso:
    # 1. Quien presente el token de seguimiento del pedido
    autorizado = False
    if token and pedido.token_seguimiento == token:
        autorizado = True

    # 2. Si viene token JWT de sesión
    if not autorizado and authorization and authorization.startswith("Bearer "):
        jwt_token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
                if user and user.activo:
                    # Operador o admin del mismo tenant
                    if user.tenant_id == tenant.id and user.rol in ("operador", "admin"):
                        autorizado = True
                    # Dueño del pedido
                    elif pedido.usuario_id == user.id:
                        autorizado = True
        except (JWTError, ValueError):
            pass

    if not autorizado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado para acceder a este archivo"
        )
    
    if not os.path.exists(archivo.path_storage):
        raise HTTPException(status_code=404, detail="El archivo físico ya no existe en el almacenamiento")
        
    return FileResponse(
        path=archivo.path_storage, 
        filename=archivo.nombre_original,
        content_disposition_type="inline"
    )
