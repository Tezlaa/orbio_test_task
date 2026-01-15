from fastapi import APIRouter
from typing import Dict

common_router = APIRouter()


@common_router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify service status.
    """
    return {"status": "ok"}
