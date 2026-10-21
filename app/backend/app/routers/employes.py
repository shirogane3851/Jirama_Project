from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Compte, Employe, RoleEnum
from schemas import EmployeCreate, EmployeRead, EmployeUpdate
from security import get_current_compte, require_roles
from utils import get_or_404, persist, remove

router = APIRouter(prefix="/employes", tags=["Employés"])

READ_ROLES = (RoleEnum.AGENT_POINTAGE, RoleEnum.VALIDATEUR_CONGE, RoleEnum.ADMIN_COMPTES)


@router.post("", response_model=EmployeRead, status_code=status.HTTP_201_CREATED)
def create_employe(
    payload: EmployeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(RoleEnum.ADMIN_COMPTES)),
):
    employe = Employe(**payload.model_dump())
    return persist(db, request, current.id, "CREATE", employe, "employe",
                   f"matricule={employe.matricule}")


@router.get("", response_model=list[EmployeRead])
def list_employes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(*READ_ROLES)),
):
    stmt = select(Employe).order_by(Employe.nom, Employe.prenom).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{employe_id}", response_model=EmployeRead)
def get_employe(
    employe_id: int,
    db: Session = Depends(get_db),
    current: Compte = Depends(get_current_compte),
):
    if current.role not in READ_ROLES and current.employe_id != employe_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé")
    return get_or_404(db, Employe, employe_id, "Employé")


@router.patch("/{employe_id}", response_model=EmployeRead)
def update_employe(
    employe_id: int,
    payload: EmployeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(RoleEnum.ADMIN_COMPTES)),
):
    employe = get_or_404(db, Employe, employe_id, "Employé")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(employe, field, value)
    return persist(db, request, current.id, "UPDATE", employe, "employe",
                   f"champs={', '.join(changes)}")


@router.delete("/{employe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employe(
    employe_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(RoleEnum.ADMIN_COMPTES)),
):
    employe = get_or_404(db, Employe, employe_id, "Employé")
    remove(db, request, current.id, employe, "employe", f"matricule={employe.matricule}")