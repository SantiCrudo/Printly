from fastapi import APIRouter
from app.api.pedidos import router as pedidos_router
from app.api.archivos import router as archivos_router
from app.api.tenant import router as tenant_router
from app.api.auth import router as auth_router
from app.api.stats import router as stats_router

api_router = APIRouter()
api_router.include_router(pedidos_router, prefix="/pedidos", tags=["pedidos"])
api_router.include_router(archivos_router, prefix="/archivos", tags=["archivos"])
api_router.include_router(tenant_router, prefix="/tenant", tags=["tenant"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(stats_router, prefix="/stats", tags=["stats"])
