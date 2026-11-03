import os
import io
import pytest
from decimal import Decimal
from app.models.pedido import Pedido
from app.models.archivo import Archivo
from app.models.sucursal import Sucursal
from app.services.counter import generar_codigo_pedido

def test_contador_codigos_secuenciales(db_session, test_tenant):
    c1 = generar_codigo_pedido(db_session, test_tenant.id)
    c2 = generar_codigo_pedido(db_session, test_tenant.id)
    c3 = generar_codigo_pedido(db_session, test_tenant.id)
    assert c1 == "PL-0001"
    assert c2 == "PL-0002"
    assert c3 == "PL-0003"

def test_flujo_pedido_invitado_y_seguimiento(client, db_session, test_tenant):
    sucursal = db_session.query(Sucursal).filter(Sucursal.tenant_id == test_tenant.id).first()
    
    # Crear archivo dummy en memoria
    file_content = b"%PDF-1.4 test dummy pdf content"
    files = {
        "archivo": ("documento.pdf", io.BytesIO(file_content), "application/pdf")
    }
    data = {
        "nombre": "Ana Gomez",
        "contacto": "1199887766",
        "desc": "Imprimir urgente",
        "copias": 2,
        "paginas": 5,
        "color": False,
        "doble_faz": True,
        "tamano": "A4",
        "sucursal_id": sucursal.id,
        "turnstile_token": "dummy-token-ok"
    }

    response = client.post(
        "/api/pedidos/invitado",
        data=data,
        files=files,
        headers={"X-Tenant-Subdomain": "demo"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert "codigo" in res_data
    assert res_data["codigo"].startswith("PL-")
    assert "token_seguimiento" in res_data
    assert res_data["precio_estimado"] > 0

    token = res_data["token_seguimiento"]
    codigo = res_data["codigo"]

    # 1. Consultar la pantalla pública de seguimiento
    res_seg = client.get(
        f"/api/pedidos/seguimiento/{token}",
        headers={"X-Tenant-Subdomain": "demo"}
    )
    assert res_seg.status_code == 200
    seg_data = res_seg.json()
    assert seg_data["codigo"] == codigo
    assert seg_data["estado"] == "recibido"
    assert seg_data["sucursal_nombre"] == "Casa Central"
    assert "documento.pdf" not in str(seg_data) # no expone paths ni nombres internos

    # 2. Token inexistente -> 404
    res_seg_404 = client.get(
        "/api/pedidos/seguimiento/token_invalido_xxx",
        headers={"X-Tenant-Subdomain": "demo"}
    )
    assert res_seg_404.status_code == 404

def test_seguridad_acceso_archivos(client, db_session, test_tenant, operator_token):
    # Crear pedido y archivo en BD
    os.makedirs("storage", exist_ok=True)
    test_file_path = os.path.join("storage", "test_file.pdf")
    with open(test_file_path, "wb") as f:
        f.write(b"Contenido confidencial")

    sucursal = db_session.query(Sucursal).filter(Sucursal.tenant_id == test_tenant.id).first()
    pedido = Pedido(
        tenant_id=test_tenant.id,
        sucursal_id=sucursal.id,
        codigo="PL-0099",
        token_seguimiento="token_secreto_abc",
        estado="recibido",
        cantidad_copias=1,
        color=False,
        tamano_papel="A4",
        doble_faz=False,
        precio_estimado=Decimal("25.00")
    )
    db_session.add(pedido)
    db_session.commit()
    db_session.refresh(pedido)

    archivo = Archivo(
        pedido_id=pedido.id,
        path_storage=test_file_path,
        nombre_original="dni_frente.pdf",
        tamano_bytes=len(b"Contenido confidencial")
    )
    db_session.add(archivo)
    db_session.commit()
    db_session.refresh(archivo)

    # A) Sin token ni autenticación -> 401 Unauthorized (bloquea IDOR)
    res_no_auth = client.get(
        f"/api/archivos/{archivo.id}",
        headers={"X-Tenant-Subdomain": "demo"}
    )
    assert res_no_auth.status_code == 401

    # B) Con token de seguimiento válido en query param -> 200 OK
    res_token = client.get(
        f"/api/archivos/{archivo.id}?token=token_secreto_abc",
        headers={"X-Tenant-Subdomain": "demo"}
    )
    assert res_token.status_code == 200
    assert res_token.content == b"Contenido confidencial"

    # C) Con rol operador -> 200 OK
    res_op = client.get(
        f"/api/archivos/{archivo.id}",
        headers={"X-Tenant-Subdomain": "demo", "Authorization": f"Bearer {operator_token}"}
    )
    assert res_op.status_code == 200
    assert res_op.content == b"Contenido confidencial"

def test_repetir_pedido_duplica_archivo_fisico(client, db_session, test_tenant, client_user, client_token):
    sucursal = db_session.query(Sucursal).filter(Sucursal.tenant_id == test_tenant.id).first()
    
    orig_path = os.path.join("storage", "original_para_repetir.pdf")
    with open(orig_path, "wb") as f:
        f.write(b"Archivo base a duplicar")

    pedido_orig = Pedido(
        tenant_id=test_tenant.id,
        sucursal_id=sucursal.id,
        usuario_id=client_user.id,
        codigo="PL-0050",
        token_seguimiento="token_50",
        estado="entregado",
        cantidad_copias=1,
        rango_paginas="3",
        color=False,
        tamano_papel="A4",
        doble_faz=False,
        precio_estimado=Decimal("75.00")
    )
    db_session.add(pedido_orig)
    db_session.commit()
    db_session.refresh(pedido_orig)

    archivo_orig = Archivo(
        pedido_id=pedido_orig.id,
        path_storage=orig_path,
        nombre_original="apunte.pdf",
        tamano_bytes=len(b"Archivo base a duplicar")
    )
    db_session.add(archivo_orig)
    db_session.commit()

    # Repetir el pedido
    res = client.post(
        f"/api/pedidos/{pedido_orig.id}/repetir",
        headers={"X-Tenant-Subdomain": "demo", "Authorization": f"Bearer {client_token}"}
    )
    assert res.status_code == 200
    nuevo_id = res.json()["id"]

    archivo_nuevo = db_session.query(Archivo).filter(Archivo.pedido_id == nuevo_id).first()
    assert archivo_nuevo is not None
    # Debe ser un archivo físico distinto en path
    assert archivo_nuevo.path_storage != orig_path
    assert os.path.exists(archivo_nuevo.path_storage)

    # Si borramos el archivo original, el nuevo no debe romperse
    os.remove(orig_path)
    assert not os.path.exists(orig_path)
    assert os.path.exists(archivo_nuevo.path_storage)
    with open(archivo_nuevo.path_storage, "rb") as f:
        assert f.read() == b"Archivo base a duplicar"

def test_stats_todos_los_estados_y_facturacion(client, db_session, test_tenant, operator_token):
    sucursal = db_session.query(Sucursal).filter(Sucursal.tenant_id == test_tenant.id).first()

    # Crear pedidos con estados normales, expirado y cancelado
    estados_test = [
        ("recibido", Decimal("100.00")),
        ("en_cola", Decimal("150.00")),
        ("imprimiendo", Decimal("200.00")),
        ("listo", Decimal("250.00")),
        ("entregado", Decimal("300.00")),
        ("expirado", Decimal("50.00")),
        ("cancelado", Decimal("70.00")),
    ]

    for i, (est, precio) in enumerate(estados_test):
        p = Pedido(
            tenant_id=test_tenant.id,
            sucursal_id=sucursal.id,
            codigo=f"PL-{str(200+i).zfill(4)}",
            estado=est,
            cantidad_copias=1,
            rango_paginas="1",
            color=False,
            tamano_papel="A4",
            doble_faz=False,
            precio_estimado=precio
        )
        db_session.add(p)
    db_session.commit()

    # Consultar stats con operador
    res = client.get(
        "/api/stats/?periodo=todos",
        headers={"X-Tenant-Subdomain": "demo", "Authorization": f"Bearer {operator_token}"}
    )
    assert res.status_code == 200
    kpis = res.json()["kpis"]

    # Facturación cobrada debe ser SOLO de los entregados (300.00)
    assert kpis["facturacion_cobrada"] == 300.00

    # Facturación estimada debe sumar no-cancelados y no-expirados (100 + 150 + 200 + 250 + 300 = 1000.00)
    assert kpis["facturacion_estimada"] == 1000.00

