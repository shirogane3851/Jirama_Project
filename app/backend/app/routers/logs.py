from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Compte, Log, RoleEnum
from schemas import LogRead
from security import require_roles

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("", response_model=list[LogRead])
def list_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    table_name: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(RoleEnum.ADMIN_COMPTES)),
):
    stmt = select(Log)
    if user_id is not None:
        stmt = stmt.where(Log.user_id == user_id)
    if action is not None:
        stmt = stmt.where(Log.action == action)
    if table_name is not None:
        stmt = stmt.where(Log.table_name == table_name)
    stmt = stmt.order_by(Log.timestamp.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()
