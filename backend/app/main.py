import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models.tenant import Tenant
from app.models.sucursal import Sucursal
from app.models.precios import PreciosConfig
from app.models.usuario import Usuario
from app.models.contador import TenantContador
from app.core.security import get_password_hash
from app.api import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("printly")

app = FastAPI(title=settings.PROJECT_NAME)

# CORS con lista explícita de orígenes (no wildcard con credenciales)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def seed_demo_data():
    """
    Siembra el tenant demo y sus datos iniciales si no existen.
    Falla ruidosamente si algo sale mal.
    """
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.subdominio == "demo").first()
        if not tenant:
            logger.info("Creando tenant demo y configuración inicial...")
            tenant = Tenant(
                subdominio="demo",
                nombre_negocio="Printly Demo",
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            
            sucursal1 = Sucursal(
                tenant_id=tenant.id,
                nombre="Casa Central",
                direccion="Av. Siempre Viva 123"
            )
            sucursal2 = Sucursal(
                tenant_id=tenant.id,
                nombre="Sucursal Centro",
                direccion="Calle Falsa 456"
            )
            db.add_all([sucursal1, sucursal2])
            
            precios = PreciosConfig(
                tenant_id=tenant.id,
                precio_bn_pagina=25.00,
                precio_color_pagina=60.00,
                recargo_a3=1.60,
                recargo_oficio=1.15,
                descuento_doble_faz=1.00
            )
            db.add(precios)

            contador = TenantContador(
                tenant_id=tenant.id,
                ultimo_codigo=0
            )
            db.add(contador)

            # Usuario operador inicial para pruebas en demo
            operador = Usuario(
                tenant_id=tenant.id,
                nombre="Operador",
                apellido="Demo",
                email="operador@printly.ar",
                password_hash=get_password_hash("operador123"),
                email_verificado=True,
                activo=True,
                rol="operador"
            )
            db.add(operador)
            
            db.commit()
            logger.info("Tenant demo sembrado exitosamente con operador: operador@printly.ar / operador123")
    except Exception as e:
        logger.error(f"Error crítico sembrando datos iniciales del tenant demo: {e}", exc_info=True)
        if settings.ENVIRONMENT not in ("development", "testing"):
            sys.exit(1)
        raise e
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    settings.validate_production()
    os.makedirs("storage", exist_ok=True)
    if settings.ENVIRONMENT != "testing":
        seed_demo_data()

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Printly API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
