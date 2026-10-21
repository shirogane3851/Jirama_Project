"""Congés et permissions : mêmes règles, donc un seul code (factory)."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Compte, Conge, Employe, Permission, RoleEnum
from schemas import (
    CongeCreate,
    CongeDecision,
    CongeRead,
    CongeUpdate,
    PermissionCreate,
    PermissionDecision,
    PermissionRead,
    PermissionUpdate,
    StatutDemande,
)
from security import get_current_compte, require_roles
from utils import get_or_404, persist, remove


def build_demande_router(
    *, model, create_schema, update_schema, decision_schema, read_schema,
    prefix: str, tag: str, label: str, table_name: str, deduct_balance: bool,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    def get_accessible(db: Session, id_: int, current: Compte):
        demande = get_or_404(db, model, id_, label)
        if demande.employe_id != current.employe_id and current.role != RoleEnum.VALIDATEUR_CONGE:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé")
        return demande

    def get_own_pending(db: Session, id_: int, current: Compte):
        demande = get_or_404(db, model, id_, label)
        if demande.employe_id != current.employe_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Vous ne pouvez modifier que vos demandes")
        if demande.statut != StatutDemande.EN_ATTENTE.value:
            raise HTTPException(status.HTTP_409_CONFLICT, "La demande a déjà été traitée")
        return demande

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def create(
        payload: create_schema,
        request: Request,
        db: Session = Depends(get_db),
        current: Compte = Depends(get_current_compte),
    ):
        if payload.employe_id != current.employe_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Vous ne pouvez faire une demande que pour vous-même")
        demande = model(**payload.model_dump())
        return persist(db, request, current.id, "CREATE", demande, table_name,
                       f"{payload.date_debut} -> {payload.date_fin}")

    @router.get("", response_model=list[read_schema])
    def list_(
        statut: Optional[StatutDemande] = None,
        employe_id: Optional[int] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db),
        current: Compte = Depends(get_current_compte),
    ):
        stmt = select(model)
        if current.role != RoleEnum.VALIDATEUR_CONGE:
            stmt = stmt.where(model.employe_id == current.employe_id)
        elif employe_id is not None:
            stmt = stmt.where(model.employe_id == employe_id)
        if statut is not None:
            stmt = stmt.where(model.statut == statut.value)
        stmt = stmt.order_by(model.created_at.desc()).offset(skip).limit(limit)
        return db.scalars(stmt).all()

    @router.get("/{id_}", response_model=read_schema)
    def get_one(
        id_: int,
        db: Session = Depends(get_db),
        current: Compte = Depends(get_current_compte),
    ):
        return get_accessible(db, id_, current)

    @router.patch("/{id_}", response_model=read_schema)
    def update(
        id_: int,
        payload: update_schema,
        request: Request,
        db: Session = Depends(get_db),
        current: Compte = Depends(get_current_compte),
    ):
        demande = get_own_pending(db, id_, current)
        changes = payload.model_dump(exclude_unset=True)
        debut = changes.get("date_debut", demande.date_debut)
        fin = changes.get("date_fin", demande.date_fin)
        if fin < debut:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "date_fin doit être postérieure ou égale à date_debut")
        for field, value in changes.items():
            setattr(demande, field, value)
        return persist(db, request, current.id, "UPDATE", demande, table_name,
                       f"champs={', '.join(changes)}")

    @router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
    def cancel(
        id_: int,
        request: Request,
        db: Session = Depends(get_db),
        current: Compte = Depends(get_current_compte),
    ):
        demande = get_own_pending(db, id_, current)
        remove(db, request, current.id, demande, table_name, "annulation par l'employé")

    @router.post("/{id_}/decision", response_model=read_schema)
    def decide(
        id_: int,
        payload: decision_schema,
        request: Request,
        db: Session = Depends(get_db),
        current: Compte = Depends(require_roles(RoleEnum.VALIDATEUR_CONGE)),
    ):
        demande = get_or_404(db, model, id_, label)
        if demande.employe_id == current.employe_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Vous ne pouvez pas traiter votre propre demande")
        if demande.statut != StatutDemande.EN_ATTENTE.value:
            raise HTTPException(status.HTTP_409_CONFLICT, "La demande a déjà été traitée")
        if payload.statut == StatutDemande.EN_ATTENTE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "La décision doit être 'approuve' ou 'refuse'")

        if payload.statut == StatutDemande.APPROUVE and deduct_balance:
            employe = get_or_404(db, Employe, demande.employe_id, "Employé")
            jours = Decimal((demande.date_fin - demande.date_debut).days + 1)
            if employe.solde_conge < jours:
                raise HTTPException(status.HTTP_409_CONFLICT, "Solde de congé insuffisant")
            employe.solde_conge -= jours

        demande.statut = payload.statut.value
        demande.proceed_at = datetime.now()
        demande.proceed_by = current.id
        return persist(db, request, current.id, "DECISION", demande, table_name,
                       f"statut={payload.statut.value}")

    return router


conge_router = build_demande_router(
    model=Conge, create_schema=CongeCreate, update_schema=CongeUpdate,
    decision_schema=CongeDecision, read_schema=CongeRead,
    prefix="/conges", tag="Congés", label="Congé", table_name="conge",
    deduct_balance=True,  # l'approbation retire les jours du solde
)

permission_router = build_demande_router(
    model=Permission, create_schema=PermissionCreate, update_schema=PermissionUpdate,
    decision_schema=PermissionDecision, read_schema=PermissionRead,
    prefix="/permissions", tag="Permissions", label="Permission", table_name="permission",
    deduct_balance=False,
)
