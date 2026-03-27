from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from jose import jwt, JWTError
from api.core.config import settings

# Paths that are completely public (no auth required)
EXCLUDED_PATHS = [
    "/api/v1/login/",
    "/api/v1/register/",
    "/docs",
    "/openapi.json",
    "/redoc",
]

# Path + method combinations that are public (e.g., GET /prompts is public, but POST/PUT/DELETE require auth)
PUBLIC_ENDPOINTS = [
    ("GET", "/api/v1/prompts/"),
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # Check for completely public paths
        if any(path.startswith(p) for p in EXCLUDED_PATHS):
            return await call_next(request)

        # Check for public path + method combinations
        if (method, path) in PUBLIC_ENDPOINTS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401, content={"detail": "Unauthorized: Missing token"}
            )

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            request.state.user = payload["sub"]
        except JWTError:
            return JSONResponse(
                status_code=401, content={"detail": "Unauthorized: Invalid token"}
            )

        return await call_next(request)
