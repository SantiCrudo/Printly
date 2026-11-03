from sqlalchemy.orm import Session
from app.models.contador import TenantContador

def generar_codigo_pedido(db: Session, tenant_id: int) -> str:
    """
    Genera el siguiente código de pedido para el tenant dado de forma segura contra concurrencia.
    En bases de datos que lo soportan (PostgreSQL), utiliza SELECT ... FOR UPDATE.
    """
    query = db.query(TenantContador).filter(TenantContador.tenant_id == tenant_id)
    if db.bind and db.bind.dialect.name != "sqlite":
        query = query.with_for_update()
        
    contador = query.first()

    if not contador:
        contador = TenantContador(tenant_id=tenant_id, ultimo_codigo=0)
        db.add(contador)
        db.flush()
        
        query = db.query(TenantContador).filter(TenantContador.tenant_id == tenant_id)
        if db.bind and db.bind.dialect.name != "sqlite":
            query = query.with_for_update()
        contador = query.first()

    contador.ultimo_codigo += 1
    db.flush()
    return f"PL-{str(contador.ultimo_codigo).zfill(4)}"
