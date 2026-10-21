from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Compte, RoleEnum
from schemas import CompteRead
from security import create_access_token, get_current_compte, verify_password
from utils import write_log

router = APIRouter(prefix="/auth", tags=["Authentification"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    compte = db.scalar(select(Compte).where(Compte.username == form.username))

    if compte is None or not verify_password(form.password, compte.password_hash):
        write_log(db, request, None, "LOGIN_FAILED", "compte", None, f"username={form.username}")
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
