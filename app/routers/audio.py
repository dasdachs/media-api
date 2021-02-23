import os.path
from pathlib import Path
from typing import cast, Dict, Optional

import av
from fastapi import APIRouter, File, Form, UploadFile, BackgroundTasks, status, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.auth import validate_api_key
from app.file_storage import clean_up, save_uploaded_file, SavedFile
from app.settings import settings


audio_router = APIRouter(prefix="/audio")


class AudioInfo(BaseModel):
    info: str
    duration: int
    fileFormat: str
    metadata: Optional[Dict[str, str]]
    size: int


@audio_router.post("/info", status_code=status.HTTP_200_OK, response_model=AudioInfo)
async def get_audio_info(
    background_tasks: BackgroundTasks,
    saved_file: SavedFile = Depends(save_uploaded_file),
) -> AudioInfo:
    """Get info about the data"""
    file = saved_file.get("file")
    if file:
        background_tasks.add_task(clean_up, file.filename)

    inp = av.open(saved_file.get("path"))

    info = AudioInfo(
        info=inp.dumps_format(),
        duration=inp.duration,
        fileFormat=inp.format.name,
        metadata=inp.metadata,
        size=inp.size,
    )

    inp.close()

    return info


@audio_router.post("/", status_code=status.HTTP_200_OK)
async def convert_audio(
    background_tasks: BackgroundTasks,
    saved_file: SavedFile = Depends(save_uploaded_file),
    outFormat: str = Form(...),
) -> FileResponse:
    f = saved_file.get("file")
    file = cast(UploadFile, f)

    if file:
        background_tasks.add_task(clean_up, file.filename)

    filename = os.path.splitext(file.filename)[0]
    inp = av.open(saved_file.get("path"))

    out_file_path = os.path.join(
        ".",
        settings.file_storage,
        settings.transformed_files_dir,
        f"{filename}.{outFormat}",
    )
    out = av.open(out_file_path, "w")

    ostream = out.add_stream(outFormat)

    for frame in inp.decode(audio=0):
        frame.pts = None

        for p in ostream.encode(frame):
            out.mux(p)

    for p in ostream.encode(None):
        out.mux(p)

    inp.close()
    out.close()

    return FileResponse(out_file_path)
