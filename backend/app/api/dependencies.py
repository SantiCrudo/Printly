import re
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.core.config import settings
from app.core.security import ALGORITHM
from jose import jwt, JWTError

IPV4_REGEX = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_tenant_subdomain(request: Request) -> str:
    """
    Resuelve el subdominio del tenant.
    En desarrollo, respeta X-Tenant-Subdomain si ALLOW_SUBDOMAIN_HEADER está habilitado.
    En producción, solo resuelve desde el header Host.
    """
    if settings.ALLOW_SUBDOMAIN_HEADER:
        header_subdomain = request.headers.get("X-Tenant-Subdomain")
        if header_subdomain:
            clean_sub = header_subdomain.strip().lower()
            if not IPV4_REGEX.match(clean_sub) and not clean_sub.isdigit():
                return clean_sub

    host = request.headers.get("host", "")
    clean_host = host.split(":")[0].strip()

    if clean_host in ("localhost", "127.0.0.1") or IPV4_REGEX.match(clean_host):
        return "demo"

    parts = clean_host.split(".")
    if len(parts) >= 3 and not parts[0].isdigit():
        return parts[0].strip().lower()

    # Default fallback para dev/local
    return "demo"

def get_current_tenant(
    db: Session = Depends(get_db), 
    subdomain: str = Depends(get_tenant_subdomain)
) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.subdominio == subdomain).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return tenant

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if not current_user.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return current_user

def require_operador_o_admin(
    current_user: Usuario = Depends(get_current_active_user),
    tenant: Tenant = Depends(get_current_tenant)
) -> Usuario:
    if current_user.tenant_id != tenant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No autorizado para este negocio"
        )
    if current_user.rol not in ("operador", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Se requiere rol de operador o administrador"
        )
    return current_user
