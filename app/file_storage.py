import os
from typing import Optional

from .settings import settings


def clean_up(file_name: Optional[str] = None):
    """Cleans up the uploaded files"""
    path = os.path.join(".", settings.file_storage, settings.uploaded_files_dir)

    files = []

    if file_name:
        files.append(os.path.join(path, file_name))
    else:
        files = [os.path.join(path, file_name) for file_name in os.listdir(path)]

    for file in files:
        os.remove(file)
