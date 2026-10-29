from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Compte, RoleEnum, Log
from schemas import CompteRead
from security import create_access_token, get_current_compte, verify_password
from utils import write_log

from datetime import datetime, timedelta
from sqlalchemy import func, select
from config import settings

router = APIRouter(prefix="/auth", tags=["Authentification"])

MAX_ECHECS = int(settings.max_echecs)
VERROU_MINUTES = int(settings.verrou_minutes)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum


def _nb_echecs(db: Session, cle: str, compte) -> int:
    """Échecs récents pour cet identifiant, depuis la dernière connexion réussie."""
    depuis = datetime.now() - timedelta(minutes=VERROU_MINUTES)
    if compte is not None:
        dernier_ok = db.scalar(
            select(func.max(Log.timestamp)).where(Log.action == "LOGIN", Log.user_id == compte.id)
        )
        if dernier_ok and dernier_ok > depuis:
            depuis = dernier_ok
    return db.scalar(
        select(func.count()).select_from(Log).where(
            Log.action == "LOGIN_FAILED", Log.details == cle, Log.timestamp > depuis
        )
    )


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    username = form.username.strip()
    cle = f"username={username[:100]}"
    compte = db.scalar(select(Compte).where(Compte.username == username))

    # Même réponse que le compte existe ou non, pour ne pas révéler les identifiants valides
    if _nb_echecs(db, cle, compte) >= MAX_ECHECS:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Trop de tentatives. Réessayez dans quelques minutes.",
            headers={"Retry-After": str(VERROU_MINUTES * 60)},
        )

    if compte is None or not verify_password(form.password, compte.password_hash):
        write_log(db, request, None, "LOGIN_FAILED", "compte", None, cle)
        db.flush()
        if _nb_echecs(db, cle, compte) == MAX_ECHECS:  # une seule ligne au moment du verrouillage
            write_log(db, request, None, "LOGIN_LOCKED", "compte", None, cle)
        db.commit()
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not compte.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Compte désactivé")

    write_log(db, request, compte.id, "LOGIN", "compte", compte.id)
    db.commit()
    return Token(access_token=create_access_token(compte.id), role=compte.role)


@router.get("/me", response_model=CompteRead)
def me(current: Compte = Depends(get_current_compte)):
    return current