from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from utils.auth import get_current_user
from fastapi import status

async def authenticate_request(request: Request, call_next):
    excluded_paths = ["/", "/token", "/docs"]
    if request.url.path in excluded_paths:
        return await call_next(request)
    try:
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token is missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = token.replace("Bearer ", "")
        await get_current_user(token)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
            headers=e.headers
        )
    return await call_next(request)