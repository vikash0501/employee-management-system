
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


def verify_api_token(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> None:
    if credentials is None or not secrets.compare_digest(
        credentials.credentials,
        settings.API_ACCESS_TOKEN,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
