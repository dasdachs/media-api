from fastapi import Depends, Header, HTTPException, status


from .settings import settings


def validate_api_key(x_api_key: str = Header(...)):
    """Gets and validates the `x-api-key` header"""
    if x_api_key != settings.api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid api key")
