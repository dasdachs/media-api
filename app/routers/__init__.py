from fastapi import APIRouter, Depends

from app.routers.audio import audio_router
from app.routers.health import health_check_router
from app.routers.video import video_router

from app.auth import validate_api_key


# API V1
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(
    audio_router,
    dependencies=[Depends(validate_api_key)],
    tags=["audio", "media"],
)
api_v1_router.include_router(health_check_router, tags=["deployment"])
api_v1_router.include_router(
    video_router,
    dependencies=[Depends(validate_api_key)],
    tags=["video", "media"],
)
