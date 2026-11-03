import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configurar entorno de testing
os.environ["ENVIRONMENT"] = "testing"
os.environ["ALLOW_SUBDOMAIN_HEADER"] = "true"
os.environ["SECRET_KEY"] = "test_secret_key_1234567890_super_secure"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.models.base import Base
import app.models
from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.models.tenant import Tenant
from app.models.sucursal import Sucursal
from app.models.precios import PreciosConfig
from app.models.usuario import Usuario
from app.models.contador import TenantContador
from app.main import app

# Base de datos SQLite en memoria para tests
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_tenant(db_session):
    tenant = Tenant(
        subdominio="demo",
        nombre_negocio="Printly Demo",
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)

    sucursal = Sucursal(
        tenant_id=tenant.id,
        nombre="Casa Central",
        direccion="Av. Siempre Viva 123"
    )
    db_session.add(sucursal)

    precios = PreciosConfig(
        tenant_id=tenant.id,
        precio_bn_pagina=25.00,
        precio_color_pagina=60.00,
        recargo_a3=1.60,
        recargo_oficio=1.15,
        descuento_doble_faz=1.00
    )
    db_session.add(precios)

    contador = TenantContador(
        tenant_id=tenant.id,
        ultimo_codigo=0
    )
    db_session.add(contador)
    db_session.commit()
    return tenant

@pytest.fixture
def operator_user(db_session, test_tenant):
    operador = Usuario(
        tenant_id=test_tenant.id,
        nombre="Operador",
        apellido="Test",
        email="operador@test.com",
        password_hash=get_password_hash("pass123"),
        email_verificado=True,
        activo=True,
        rol="operador"
    )
    db_session.add(operador)
    db_session.commit()
    db_session.refresh(operador)
    return operador

@pytest.fixture
def operator_token(operator_user):
    return create_access_token(data={"sub": str(operator_user.id), "rol": operator_user.rol})

@pytest.fixture
def client_user(db_session, test_tenant):
    cliente = Usuario(
        tenant_id=test_tenant.id,
        nombre="Juan",
        apellido="Perez",
        email="juan@test.com",
        password_hash=get_password_hash("pass123"),
        email_verificado=True,
        activo=True,
        rol="cliente"
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    return cliente

@pytest.fixture
def client_token(client_user):
    return create_access_token(data={"sub": str(client_user.id), "rol": client_user.rol})
