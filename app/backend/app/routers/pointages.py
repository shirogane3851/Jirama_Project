from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Avertissement, Compte, Employe, Pointage, RoleEnum
from schemas import (
    AvertissementCreate,
    AvertissementLift,
    AvertissementRead,
    PointageCreate,
    PointageRead,
    StatutAvertissement,
    TypePointage,
)
from security import get_current_compte, require_roles
from utils import get_or_404, persist

# Rôles qui voient les données de tous les employés (les autres voient les leurs)
VIEW_ALL = (RoleEnum.AGENT_POINTAGE, RoleEnum.VALIDATEUR_CONGE)
# Rôles qui peuvent lever un avertissement
LIFT_ROLES = (RoleEnum.AGENT_POINTAGE, RoleEnum.VALIDATEUR_CONGE)

pointage_router = APIRouter(prefix="/pointages", tags=["Pointages"])
avertissement_router = APIRouter(prefix="/avertissements", tags=["Avertissements"])


# ------------------------------------------------------------- pointages
@pointage_router.post("", response_model=PointageRead, status_code=status.HTTP_201_CREATED)
def create_pointage(
    payload: PointageCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(RoleEnum.AGENT_POINTAGE)),
):
    get_or_404(db, Employe, payload.employe_id, "Employé")
    data = {
        "employe_id": payload.employe_id,
        "admin_id": current.id,  # l'agent connecté, jamais fourni par le client
        "type": payload.type.value,
    }
    if payload.timestamp is not None:
        data["timestamp"] = payload.timestamp
    pointage = Pointage(**data)
    return persist(db, request, current.id, "CREATE", pointage, "pointage",
                   f"employe_id={payload.employe_id}, type={payload.type.value}")


@pointage_router.get("", response_model=list[PointageRead])
def list_pointages(
    employe_id: Optional[int] = None,
    type: Optional[TypePointage] = None,
    du: Optional[date] = None,
    au: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current: Compte = Depends(get_current_compte),
):
    stmt = select(Pointage)
    if current.role in VIEW_ALL:
        if employe_id is not None:
            stmt = stmt.where(Pointage.employe_id == employe_id)
    else:
        stmt = stmt.where(Pointage.employe_id == current.employe_id)
    if type is not None:
        stmt = stmt.where(Pointage.type == type.value)
    if du is not None:
        stmt = stmt.where(Pointage.timestamp >= datetime.combine(du, time.min))
    if au is not None:
        stmt = stmt.where(Pointage.timestamp <= datetime.combine(au, time.max))
    stmt = stmt.order_by(Pointage.timestamp.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@pointage_router.get("/{pointage_id}", response_model=PointageRead)
def get_pointage(
    pointage_id: int,
    db: Session = Depends(get_db),
    current: Compte = Depends(get_current_compte),
):
    pointage = get_or_404(db, Pointage, pointage_id, "Pointage")
    if current.role not in VIEW_ALL and pointage.employe_id != current.employe_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé")
    return pointage


# ------------------------------------------------------------- avertissements
@avertissement_router.post("", response_model=AvertissementRead, status_code=status.HTTP_201_CREATED)
def create_avertissement(
    payload: AvertissementCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(RoleEnum.AGENT_POINTAGE)),
):
    get_or_404(db, Employe, payload.employe_id, "Employé")
    if payload.pointage_id is not None:
        pointage = get_or_404(db, Pointage, payload.pointage_id, "Pointage")
        if pointage.employe_id != payload.employe_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "Ce pointage n'appartient pas à cet employé")
    data = payload.model_dump()
    data["type"] = payload.type.value
    avertissement = Avertissement(**data)
    return persist(db, request, current.id, "CREATE", avertissement, "avertissement",
                   f"employe_id={payload.employe_id}, type={payload.type.value}")


@avertissement_router.get("", response_model=list[AvertissementRead])
def list_avertissements(
    employe_id: Optional[int] = None,
    statut: Optional[StatutAvertissement] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current: Compte = Depends(get_current_compte),
):
    stmt = select(Avertissement)
    if current.role in VIEW_ALL:
        if employe_id is not None:
            stmt = stmt.where(Avertissement.employe_id == employe_id)
    else:
        stmt = stmt.where(Avertissement.employe_id == current.employe_id)
    if statut is not None:
        stmt = stmt.where(Avertissement.statut == statut.value)
    stmt = stmt.order_by(Avertissement.created_at.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@avertissement_router.get("/{avertissement_id}", response_model=AvertissementRead)
def get_avertissement(
    avertissement_id: int,
    db: Session = Depends(get_db),
    current: Compte = Depends(get_current_compte),
):
    avertissement = get_or_404(db, Avertissement, avertissement_id, "Avertissement")
    if current.role not in VIEW_ALL and avertissement.employe_id != current.employe_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé")
    return avertissement


@avertissement_router.post("/{avertissement_id}/lift", response_model=AvertissementRead)
def lift_avertissement(
    avertissement_id: int,
    payload: AvertissementLift,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(*LIFT_ROLES)),
):
    avertissement = get_or_404(db, Avertissement, avertissement_id, "Avertissement")
    if avertissement.statut != StatutAvertissement.ACTIF.value:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cet avertissement n'est plus actif")
    avertissement.statut = StatutAvertissement.LEVE.value
    avertissement.lifted_at = datetime.now()
    avertissement.lifted_by = current.id
    avertissement.lifted_reason = payload.lifted_reason
    return persist(db, request, current.id, "LIFT", avertissement, "avertissement",
                   payload.lifted_reason)
