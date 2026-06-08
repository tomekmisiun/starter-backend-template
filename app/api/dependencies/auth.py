from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


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
        payload = decode_token(token)
        token_type = payload.get("type")
        user_id = payload.get("sub")

        if token_type != "access" or user_id is None:
            raise credentials_exception
        parsed_user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == parsed_user_id).first()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_role(required_role: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return checker
