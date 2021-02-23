import os
from pathlib import Path
from typing import Optional, TypedDict

from fastapi import File, UploadFile, HTTPException, status

from .settings import settings


class SavedFile(TypedDict):
    path: str
    file: UploadFile


def clean_up(file_name: Optional[str] = None) -> int:
    """Cleans up the uploaded files"""
    path = os.path.join(".", settings.file_storage, settings.uploaded_files_dir)

    files = []

    if file_name:
        files.append(os.path.join(path, file_name))
    else:
        files = [os.path.join(path, file_name) for file_name in os.listdir(path)]

    for file in files:
        os.remove(file)

    return len(files)


async def save_uploaded_file(file: UploadFile = File(...)) -> SavedFile:
    """Saves the uploaded files to a temp storage"""
    try:
        p = Path(".", settings.file_storage, settings.uploaded_files_dir, file.filename)

        content = await file.read()
        p.write_bytes(content)

        return {"path": str(p.resolve()), "file": file}
    except OSError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save file to storage",
        )
