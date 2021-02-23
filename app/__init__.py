from pathlib import Path

from fastapi import FastAPI, Depends

from .auth import validate_api_key
from .file_storage import clean_up
from .middleware import SecureHeadersMiddleware
from .routers import audio_router, video_router
from .settings import settings


def app_factory():
    app = FastAPI()

    @app.on_event("startup")
    async def create_dirs_and_cleanup_files():
        Path(".", settings.file_storage, settings.uploaded_files_dir).mkdir(
            parents=True, exist_ok=True
        )
        Path(".", settings.file_storage, settings.transformed_files_dir).mkdir(
            parents=True, exist_ok=True
        )
        clean_up()

    app.add_middleware(SecureHeadersMiddleware)
    app.include_router(audio_router)
    app.include_router(video_router)

    @app.get("/api/v1/test")
    async def test_path(valid_api_key: None = Depends(validate_api_key)):
        return {"authenticated": "yes"}

    return app
