from starlette.middleware.base import BaseHTTPMiddleware

from secure import SecureHeaders


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    secure_headers = SecureHeaders()

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        SecureHeadersMiddleware.secure_headers.starlette(response)
        return response
