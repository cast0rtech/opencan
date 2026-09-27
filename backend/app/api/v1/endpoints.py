from typing import Dict, Any
from fastapi import APIRouter, Request
from app.config import settings

router = APIRouter(prefix="/api/v1")


@router.get("/status", response_model=Dict[str, Any])
async def get_system_status(request: Request):
    """Devuelve el estado instantáneo de todos los inversores monitorizados."""
    orchestrator = getattr(request.app.state, "orchestrator", None)
    inverters_summary = orchestrator.get_status_summary() if orchestrator else {}

    return {
        "status": "healthy",
        "inverters_total": len(inverters_summary),
        "inverters": inverters_summary
    }


@router.get("/config")
async def get_active_config():
    """Retorna la configuración activa del sistema."""
    return {
        "app_name": settings.app_name,
        "inverters": [inv.model_dump() for inv in settings.inverters],
        "storage": {
            "buffer_flush_seconds": settings.storage.buffer_flush_seconds,
            "retention_days": settings.storage.retention_days
        }
    }
