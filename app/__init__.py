from pathlib import Path

from fastapi import FastAPI, Depends

from .auth import validate_api_key
from .file_storage import clean_up
from .middleware import SecureHeadersMiddleware
from .routers import api_v1_router
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
    app.include_router(api_v1_router)

    return app
