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


video_router = APIRouter(prefix="/video")


class VideoInfo(BaseModel):
    info: str
    duration: int
    fileFormat: str
    metadata: Optional[Dict[str, str]]
    size: int


@video_router.post("/info", status_code=status.HTTP_200_OK, response_model=VideoInfo)
async def get_video_info(
    background_tasks: BackgroundTasks,
    saved_file: SavedFile = Depends(save_uploaded_file),
) -> VideoInfo:
    """Get info about the video"""
    file = saved_file.get("file")
    if file:
        background_tasks.add_task(clean_up, file.filename)

    inp = av.open(saved_file.get("path"))

    info = VideoInfo(
        info=inp.dumps_format(),
        duration=inp.duration,
        fileFormat=inp.format.name,
        metadata=inp.metadata,
        size=inp.size,
    )

    inp.close()

    return info


@video_router.post("/", status_code=status.HTTP_200_OK)
async def convert_video(
    background_tasks: BackgroundTasks,
    saved_file: SavedFile = Depends(save_uploaded_file),
    outFormat: str = Form(...),
    removeSubtitles: Optional[bool] = Form(False),
    removeSound: Optional[bool] = Form(False),
) -> FileResponse:
    """Covert video file"""
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

    for stream in inp.streams:
        if (stream.type == "audio" and removeSound) or (
            stream.type == "subtitle" and removeSubtitles
        ):
            continue

        out_stream = out.add_stream(template=stream)

        for packet in inp.demux(stream):
            if packet.dts is None:
                continue

            packet.stream = out_stream

            out.mux(packet)

    inp.close()
    out.close()

    return FileResponse(out_file_path)
