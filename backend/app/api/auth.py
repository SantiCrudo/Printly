from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.api.dependencies import get_current_tenant, get_current_active_user
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.sesion import SesionVerificacion
from app.core.security import get_password_hash, verify_password, create_access_token, generate_verification_token
from app.core.email import send_verification_email

router = APIRouter()

class RegistroSchema(BaseModel):
    nombre: str
    apellido: str = ""
    email: str
    telefono: Optional[str] = None
    password: str

@router.post("/registro")
def registrar_usuario(
    payload: RegistroSchema, 
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    try:
        valid = validate_email(payload.email, check_deliverability=False)
        email = valid.normalized.lower()
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    existing = db.query(Usuario).filter(
        Usuario.email == email, 
        Usuario.tenant_id == tenant.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado en este comercio")

    nuevo_usuario = Usuario(
        tenant_id=tenant.id,
        nombre=payload.nombre.strip(),
        apellido=payload.apellido.strip(),
        email=email,
        telefono=payload.telefono,
        password_hash=get_password_hash(payload.password),
        email_verificado=False,
        activo=True,
        rol="cliente"
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Crear token de verificación válido por 24 horas
    token = generate_verification_token()
    expira_en = datetime.utcnow() + timedelta(hours=24)
    sesion_verif = SesionVerificacion(
        tenant_id=tenant.id,
        usuario_id=nuevo_usuario.id,
        token=token,
        tipo="registro_mail",
        usado=False,
        expira_en=expira_en
    )
    db.add(sesion_verif)
    db.commit()

    # Mandar email (mocked en dev)
    send_verification_email(email, token, tenant.subdominio)

    return {"message": "Usuario creado. Revisá tu email para verificar la cuenta."}

@router.get("/verificar/{token}")
def verificar_email(token: str, db: Session = Depends(get_db)):
    sesion = db.query(SesionVerificacion).filter(
        SesionVerificacion.token == token, 
        SesionVerificacion.usado == False
    ).first()
    if not sesion:
        raise HTTPException(status_code=400, detail="Token inválido o ya usado")

    # Validar expiración de 24 horas
    if sesion.expira_en.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El link de verificación ha expirado. Solicitá uno nuevo.")

    usuario = db.query(Usuario).filter(Usuario.id == sesion.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.email_verificado = True
    sesion.usado = True
    db.commit()

    return {"message": "Email verificado correctamente. Ya podés iniciar sesión."}

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    email = form_data.username.lower().strip()
    usuario = db.query(Usuario).filter(
        Usuario.email == email, 
        Usuario.tenant_id == tenant.id
    ).first()

    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
        
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Tu cuenta está desactivada")

    if not usuario.email_verificado:
        raise HTTPException(status_code=400, detail="Por favor verificá tu email antes de iniciar sesión")

    access_token = create_access_token(data={"sub": str(usuario.id), "rol": usuario.rol})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "email": usuario.email,
            "rol": usuario.rol
        }
    }

@router.get("/me")
def get_mi_perfil(user: Usuario = Depends(get_current_active_user)):
    return {
        "id": user.id,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "email": user.email,
        "telefono": user.telefono,
        "rol": user.rol,
        "email_verificado": user.email_verificado
    }
