import pytest
from datetime import datetime, timedelta
from app.models.sesion import SesionVerificacion
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.core.security import get_password_hash, create_access_token

def test_registro_usuario_exitoso(client, db_session, test_tenant):
    response = client.post(
        "/api/auth/registro",
        json={
            "nombre": "Carlos",
            "apellido": "Gardel",
            "email": "carlos@test.com",
            "telefono": "1122334455",
            "password": "Password123!"
        },
        headers={"X-Tenant-Subdomain": "demo"}
    )
    assert response.status_code == 200
    assert "Usuario creado" in response.json()["message"]

    # Verificar en la base de datos
    user = db_session.query(Usuario).filter(Usuario.email == "carlos@test.com").first()
    assert user is not None
    assert user.nombre == "Carlos"
    assert user.apellido == "Gardel"
    assert user.email_verificado is False
    assert user.rol == "cliente"

    # Verificar sesión creada con expiración a 24 horas
    sesion = db_session.query(SesionVerificacion).filter(SesionVerificacion.usuario_id == user.id).first()
    assert sesion is not None
    assert sesion.usado is False
    assert sesion.token is not None

def test_registro_email_duplicado_mismo_tenant(client, test_tenant, client_user):
    response = client.post(
        "/api/auth/registro",
        json={
            "nombre": "Otro",
            "apellido": "Usuario",
            "email": client_user.email,
            "password": "Password123!"
        },
        headers={"X-Tenant-Subdomain": "demo"}
    )
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"]

def test_verificar_email_token_expirado(client, db_session, test_tenant, client_user):
    sesion_expirada = SesionVerificacion(
        tenant_id=test_tenant.id,
        usuario_id=client_user.id,
        token="token_viejo_expirado",
        tipo="registro_mail",
        usado=False,
        expira_en=datetime.utcnow() - timedelta(hours=1)
    )
    db_session.add(sesion_expirada)
    db_session.commit()

    response = client.get("/api/auth/verificar/token_viejo_expirado")
    assert response.status_code == 400
    assert "ha expirado" in response.json()["detail"]

def test_verificar_email_valido(client, db_session, test_tenant):
    user = Usuario(
        tenant_id=test_tenant.id,
        nombre="Verif",
        apellido="User",
        email="verif@test.com",
        password_hash=get_password_hash("pass"),
        email_verificado=False,
        activo=True
    )
    db_session.add(user)
    db_session.commit()

    sesion = SesionVerificacion(
        tenant_id=test_tenant.id,
        usuario_id=user.id,
        token="token_valido_123",
        tipo="registro_mail",
        usado=False,
        expira_en=datetime.utcnow() + timedelta(hours=24)
    )
    db_session.add(sesion)
    db_session.commit()

    response = client.get("/api/auth/verificar/token_valido_123")
    assert response.status_code == 200
    assert "verificado correctamente" in response.json()["message"]

    db_session.refresh(user)
    assert user.email_verificado is True

    # Intentar usar de nuevo debe fallar
    response2 = client.get("/api/auth/verificar/token_valido_123")
    assert response2.status_code == 400

def test_endpoints_negocio_autorizacion(client, test_tenant, operator_token, client_token):
    # 1. Sin autenticación -> 401
    res_no_auth = client.get("/api/pedidos/", headers={"X-Tenant-Subdomain": "demo"})
    assert res_no_auth.status_code == 401

    res_stats_no_auth = client.get("/api/stats/", headers={"X-Tenant-Subdomain": "demo"})
    assert res_stats_no_auth.status_code == 401

    # 2. Con rol cliente -> 403 Forbidden
    res_client = client.get(
        "/api/pedidos/", 
        headers={"X-Tenant-Subdomain": "demo", "Authorization": f"Bearer {client_token}"}
    )
    assert res_client.status_code == 403
    assert "operador" in res_client.json()["detail"].lower()

    # 3. Con rol operador -> 200 OK
    res_op = client.get(
        "/api/pedidos/", 
        headers={"X-Tenant-Subdomain": "demo", "Authorization": f"Bearer {operator_token}"}
    )
    assert res_op.status_code == 200

def test_autorizacion_cross_tenant(client, db_session, operator_user, operator_token):
    # Crear un segundo tenant
    otro_tenant = Tenant(subdominio="otro", nombre_negocio="Otro Negocio")
    db_session.add(otro_tenant)
    db_session.commit()

    # El operador del tenant 1 intenta consultar pedidos del tenant 2 -> 403 o 404
    res = client.get(
        "/api/pedidos/",
        headers={"X-Tenant-Subdomain": "otro", "Authorization": f"Bearer {operator_token}"}
    )
    assert res.status_code == 403
    assert "No autorizado para este negocio" in res.json()["detail"]

