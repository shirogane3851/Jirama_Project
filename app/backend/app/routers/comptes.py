from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Compte, Employe, RoleEnum
from schemas import CompteCreate, CompteRead, CompteUpdate
from security import hash_password, require_roles
from utils import get_or_404, persist

router = APIRouter(prefix="/comptes", tags=["Comptes"])

ADMIN = require_roles(RoleEnum.ADMIN_COMPTES)


@router.post("", response_model=CompteRead, status_code=status.HTTP_201_CREATED)
def create_compte(
    payload: CompteCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(ADMIN),
):
    get_or_404(db, Employe, payload.employe_id, "Employé")
    compte = Compte(
        **payload.model_dump(exclude={"password"}),
        password_hash=hash_password(payload.password),
    )
    return persist(db, request, current.id, "CREATE", compte, "compte",
                   f"username={compte.username}, role={compte.role.value}")


@router.get("", response_model=list[CompteRead])
def list_comptes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current: Compte = Depends(ADMIN),
):
    stmt = select(Compte).order_by(Compte.username).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{compte_id}", response_model=CompteRead)
def get_compte(
    compte_id: int,
    db: Session = Depends(get_db),
    current: Compte = Depends(ADMIN),
):
    return get_or_404(db, Compte, compte_id, "Compte")


@router.patch("/{compte_id}", response_model=CompteRead)
def update_compte(
    compte_id: int,
    payload: CompteUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(ADMIN),
):
    compte = get_or_404(db, Compte, compte_id, "Compte")
    changes = payload.model_dump(exclude_unset=True)

    if compte.id == current.id and (
        changes.get("is_active") is False
        or ("role" in changes and changes["role"] != RoleEnum.ADMIN_COMPTES)
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Vous ne pouvez pas désactiver votre compte ni retirer votre propre rôle admin",
        )

    if "password" in changes:
        compte.password_hash = hash_password(changes.pop("password"))
        changed = list(changes) + ["password"]
    else:
        changed = list(changes)
    for field, value in changes.items():
        setattr(compte, field, value)

    # Pas de mot de passe dans les logs : seulement les noms des champs modifiés
    return persist(db, request, current.id, "UPDATE", compte, "compte",
                   f"champs={', '.join(changed)}")
