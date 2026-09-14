import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Re-fetch from the DB instead of trusting the token's `role` claim: costs one extra
    # query per request, but means a role change takes effect on the next request without
    # needing token-revocation infrastructure. Reasonable tradeoff for short-lived access
    # tokens with no refresh-token flow.
    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user


def require_role(required_role: UserRole):
    def _require_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires the '{required_role.value}' role",
            )
        return current_user

    return _require_role


require_provider = require_role(UserRole.PROVIDER)
