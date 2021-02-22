import os.path
from pathlib import Path
from typing import Optional, Dict

import av
from fastapi import APIRouter, File, Form, UploadFile, BackgroundTasks
from pydantic import BaseModel

from fastapi.responses import FileResponse

from ..settings import settings
from ..file_storage import clean_up


audio_router = APIRouter(prefix="/api/v1/audio", tags=["audio"])


class AudioInfo(BaseModel):
    info: str
    duration: int
    fileFormat: str
    metadata: Optional[Dict[str, str]]
    size: int


# TODO: move shared logic to dependencies
@audio_router.post("/info", response_model=AudioInfo)
async def get_audio_info(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    """Get info about the data"""
    background_tasks.add_task(clean_up, file.filename)
    p = Path(".", settings.file_storage, settings.uploaded_files_dir, file.filename)
    content = await file.read()
    p.write_bytes(content)
    inp = av.open(
        os.path.join(
            ".", settings.file_storage, settings.uploaded_files_dir, file.filename
        )
    )

    info = AudioInfo(
        info=inp.dumps_format(),
        duration=inp.duration,
        fileFormat=inp.format.name,
        metadata=inp.metadata,
        size=inp.size,
    )

    inp.close()

    return info


@audio_router.post("/")
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