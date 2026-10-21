"""Modèles SQLAlchemy 2.0 pour le projet Jirama (PostgreSQL)."""
import enum
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class RoleEnum(str, enum.Enum):
    EMPLOYE = "EMPLOYE"
    AGENT_POINTAGE = "AGENT_POINTAGE"
    VALIDATEUR_CONGE = "VALIDATEUR_CONGE"
    ADMIN_COMPTES = "ADMIN_COMPTES"


# ---------------------------------------------------------------- employe
class Employe(Base):
    __tablename__ = "employe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    matricule: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    telephone: Mapped[Optional[str]] = mapped_column(String(14), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    date_embauche: Mapped[Optional[datetime]] = mapped_column(DateTime)
    photo_identite: Mapped[Optional[str]] = mapped_column(String(255))
    solde_conge: Mapped[Decimal] = mapped_column(
        Numeric(4, 1), nullable=False, default=0, server_default="0"
    )

    compte: Mapped[Optional["Compte"]] = relationship(
        back_populates="employe", uselist=False
    )
    conges: Mapped[List["Conge"]] = relationship(back_populates="employe")
    permissions: Mapped[List["Permission"]] = relationship(back_populates="employe")
    pointages: Mapped[List["Pointage"]] = relationship(back_populates="employe")
    avertissements: Mapped[List["Avertissement"]] = relationship(
        back_populates="employe", foreign_keys="Avertissement.employe_id"
    )


# ---------------------------------------------------------------- compte
class Compte(Base):
    __tablename__ = "compte"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    employe_id: Mapped[int] = mapped_column(
        ForeignKey("employe.id"), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        SAEnum(RoleEnum, name="role_enum", create_type=False), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    employe: Mapped["Employe"] = relationship(back_populates="compte")
    pointages_saisis: Mapped[List["Pointage"]] = relationship(
        back_populates="admin", foreign_keys="Pointage.admin_id"
    )
    conges_traites: Mapped[List["Conge"]] = relationship(
        back_populates="traite_par", foreign_keys="Conge.proceed_by"
    )
    permissions_traitees: Mapped[List["Permission"]] = relationship(
        back_populates="traite_par", foreign_keys="Permission.proceed_by"
    )
    avertissements_leves: Mapped[List["Avertissement"]] = relationship(
        back_populates="leve_par", foreign_keys="Avertissement.lifted_by"
    )
    logs: Mapped[List["Log"]] = relationship(back_populates="user")


# ---------------------------------------------------------------- conge
class Conge(Base):
    __tablename__ = "conge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employe_id: Mapped[int] = mapped_column(ForeignKey("employe.id"), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    motif: Mapped[Optional[str]] = mapped_column(String(100))
    statut: Mapped[str] = mapped_column(
        String(15), nullable=False, default="en_attente", server_default="en_attente"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    proceed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    proceed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("compte.id"))

    employe: Mapped["Employe"] = relationship(back_populates="conges")
    traite_par: Mapped[Optional["Compte"]] = relationship(
        back_populates="conges_traites", foreign_keys=[proceed_by]
    )


# ---------------------------------------------------------------- permission
class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employe_id: Mapped[int] = mapped_column(ForeignKey("employe.id"), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    motif: Mapped[Optional[str]] = mapped_column(String(100))
    statut: Mapped[str] = mapped_column(
        String(15), nullable=False, default="en_attente", server_default="en_attente"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    proceed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    proceed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("compte.id"))

    employe: Mapped["Employe"] = relationship(back_populates="permissions")
    traite_par: Mapped[Optional["Compte"]] = relationship(
        back_populates="permissions_traitees", foreign_keys=[proceed_by]
    )


# ---------------------------------------------------------------- pointage
class Pointage(Base):
    __tablename__ = "pointage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employe_id: Mapped[int] = mapped_column(ForeignKey("employe.id"), nullable=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey("compte.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(6), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    employe: Mapped["Employe"] = relationship(back_populates="pointages")
    admin: Mapped["Compte"] = relationship(
        back_populates="pointages_saisis", foreign_keys=[admin_id]
    )
    avertissements: Mapped[List["Avertissement"]] = relationship(
        back_populates="pointage"
    )


# ---------------------------------------------------------------- avertissement
class Avertissement(Base):
    __tablename__ = "avertissement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pointage_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pointage.id"))
    employe_id: Mapped[int] = mapped_column(ForeignKey("employe.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    date_concernee: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    motif: Mapped[Optional[str]] = mapped_column(String(100))
    statut: Mapped[str] = mapped_column(
        String(15), nullable=False, default="actif", server_default="actif"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    lifted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    lifted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("compte.id"))
    lifted_reason: Mapped[Optional[str]] = mapped_column(String(255))

    pointage: Mapped[Optional["Pointage"]] = relationship(
        back_populates="avertissements"
    )
    employe: Mapped["Employe"] = relationship(
        back_populates="avertissements", foreign_keys=[employe_id]
    )
    leve_par: Mapped[Optional["Compte"]] = relationship(
        back_populates="avertissements_leves", foreign_keys=[lifted_by]
    )


# ---------------------------------------------------------------- log
class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("compte.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    table_name: Mapped[Optional[str]] = mapped_column(String(100))
    record_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    user: Mapped[Optional["Compte"]] = relationship(back_populates="logs")