import os.path
from pathlib import Path
from typing import Optional, Dict

import av
from fastapi import APIRouter, File, Form, UploadFile, BackgroundTasks, status, Depends
from pydantic import BaseModel

from fastapi.responses import FileResponse

from ..settings import settings
from ..file_storage import clean_up, save_uploaded_file


audio_router = APIRouter(prefix="/api/v1/audio", tags=["audio"])


class AudioInfo(BaseModel):
    info: str
    duration: int
    fileFormat: str
    metadata: Optional[Dict[str, str]]
    size: int


@audio_router.post("/info", status_code=status.HTTP_200_OK, response_model=AudioInfo)
async def get_audio_info(
    background_tasks: BackgroundTasks, saved_file: str = Depends(save_uploaded_file)
):
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
    file: UploadFile = File(...),
    outFormat: str = Form(...),
) -> None:
    # Save files to tmp folder and initiate cleanup task
    background_tasks.add_task(clean_up, file.filename)
    p = Path(".", settings.file_storage, settings.uploaded_files_dir, file.filename)
    content = await file.read()
    p.write_bytes(content)

    # Transform the file
    filename = os.path.splitext(file.filename)[0]
    inp = av.open(
        os.path.join(
            ".", settings.file_storage, settings.uploaded_files_dir, file.filename
        )
    )
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