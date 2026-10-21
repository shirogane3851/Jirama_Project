from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Log


def write_log(
    db: Session,
    request: Request,
    user_id: Optional[int],
    action: str,
    table_name: Optional[str] = None,
    record_id: Optional[int] = None,
    details: Optional[str] = None,
) -> None:
    """Ajoute une ligne dans la table log (le commit est fait par l'appelant)."""
    db.add(
        Log(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            details=details[:500] if details else None,
            ip_address=request.client.host if request.client else None,
        )
    )


def _conflict(exc: IntegrityError) -> HTTPException:
    return HTTPException(
        status.HTTP_409_CONFLICT,
        "Conflit : valeur déjà utilisée ou données liées existantes",
    )


def persist(
    db: Session,
    request: Request,
    user_id: Optional[int],
    action: str,
    obj,
    table_name: str,
    details: Optional[str] = None,
):
    """Enregistre un objet (nouveau ou modifié) et son log dans la même transaction."""
    try:
        db.add(obj)
        db.flush()  # génère l'id et déclenche les contraintes
        write_log(db, request, user_id, action, table_name, obj.id, details)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _conflict(exc) from exc
    db.refresh(obj)
    return obj


def remove(
    db: Session,
    request: Request,
    user_id: Optional[int],
    obj,
    table_name: str,
    details: Optional[str] = None,
) -> None:
    """Supprime un objet et enregistre le log dans la même transaction."""
    record_id = obj.id
    try:
        db.delete(obj)
        write_log(db, request, user_id, "DELETE", table_name, record_id, details)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _conflict(exc) from exc


def get_or_404(db: Session, model, id_: int, label: str):
    obj = db.get(model, id_)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{label} introuvable")
    return obj
