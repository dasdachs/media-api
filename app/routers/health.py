from fastapi import APIRouter, status
from pydantic import BaseModel

health_check_router = APIRouter(prefix="/_health")


class HealthyResponse(BaseModel):
    status: str


@health_check_router.get(
    "/", status_code=status.HTTP_200_OK, response_model=HealthyResponse
)
async def health_check():
    return HealthyResponse(ok="All good")
