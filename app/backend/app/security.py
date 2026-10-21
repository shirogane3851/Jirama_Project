import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import Compte, RoleEnum
from config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(compte_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(compte_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_compte(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Compte:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou session expirée",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        compte_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise credentials_error

    compte = db.get(Compte, compte_id)
    if compte is None or not compte.is_active:
        raise credentials_error
    return compte


def require_roles(*roles: RoleEnum):
    """Dépendance : autorise uniquement les comptes ayant l'un des rôles donnés."""

    def checker(compte: Compte = Depends(get_current_compte)) -> Compte:
        if compte.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé pour votre rôle")
        return compte

    return checker
