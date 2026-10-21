from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
)

from models import RoleEnum


class ORMModel(BaseModel):
    """Base pour les schémas de lecture (from_attributes = lecture depuis SQLAlchemy)."""

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- enums
# Valeurs à adapter à ta logique métier (colonnes varchar côté SQL).
class StatutDemande(str, Enum):
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REFUSE = "refuse"


class TypePointage(str, Enum):  # varchar(6)
    ENTREE = "entree"
    SORTIE = "sortie"


class TypeAvertissement(str, Enum):  # varchar(20)
    RETARD = "retard"
    ABSENCE = "absence"


class StatutAvertissement(str, Enum):  # varchar(15)
    ACTIF = "actif"
    LEVE = "leve"


# ---------------------------------------------------------------- employe
class EmployeBase(BaseModel):
    nom: str = Field(..., max_length=100)
    prenom: str = Field(..., max_length=100)
    matricule: str = Field(..., max_length=15)
    telephone: Optional[str] = Field(None, max_length=14)
    email: Optional[EmailStr] = Field(None, max_length=100)
    date_embauche: Optional[datetime] = None
    photo_identite: Optional[str] = Field(None, max_length=255)


class EmployeCreate(EmployeBase):
    solde_conge: Decimal = Field(Decimal("0"), ge=0, max_digits=4, decimal_places=1)


class EmployeUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    matricule: Optional[str] = Field(None, max_length=15)
    telephone: Optional[str] = Field(None, max_length=14)
    email: Optional[EmailStr] = Field(None, max_length=100)
    date_embauche: Optional[datetime] = None
    photo_identite: Optional[str] = Field(None, max_length=255)
    solde_conge: Optional[Decimal] = Field(None, ge=0, max_digits=4, decimal_places=1)


class EmployeRead(EmployeBase, ORMModel):
    id: int
    solde_conge: Decimal


# ---------------------------------------------------------------- compte
class CompteBase(BaseModel):
    username: str = Field(..., max_length=50)
    employe_id: int
    role: RoleEnum


class CompteCreate(CompteBase):
    password: str = Field(..., min_length=8, max_length=128)  # hashé avant stockage


class CompteUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


class CompteRead(CompteBase, ORMModel):  # password_hash n'est jamais exposé
    id: int
    is_active: bool
    created_at: datetime


# ---------------------------------------------------------------- conge / permission
class _PeriodeBase(BaseModel):
    date_debut: date
    date_fin: date
    motif: Optional[str] = Field(None, max_length=100)

    @model_validator(mode="after")
    def _check_dates(self):
        if self.date_fin < self.date_debut:
            raise ValueError("date_fin doit être postérieure ou égale à date_debut")
        return self


class CongeCreate(_PeriodeBase):
    employe_id: int


class CongeUpdate(BaseModel):
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    motif: Optional[str] = Field(None, max_length=100)


class CongeDecision(BaseModel):
    """Validation / refus par un VALIDATEUR_CONGE."""

    statut: StatutDemande


class CongeRead(_PeriodeBase, ORMModel):
    id: int
    employe_id: int
    statut: StatutDemande
    created_at: datetime
    proceed_at: Optional[datetime] = None
    proceed_by: Optional[int] = None


class PermissionCreate(_PeriodeBase):
    employe_id: int


class PermissionUpdate(CongeUpdate):
    pass


class PermissionDecision(CongeDecision):
    pass


class PermissionRead(_PeriodeBase, ORMModel):
    id: int
    employe_id: int
    statut: StatutDemande
    created_at: datetime
    proceed_at: Optional[datetime] = None
    proceed_by: Optional[int] = None


# ---------------------------------------------------------------- pointage
class PointageCreate(BaseModel):
    employe_id: int
    type: TypePointage
    timestamp: Optional[datetime] = None  # défaut serveur = now()
    # admin_id est déduit du compte connecté (AGENT_POINTAGE), pas du client


class PointageRead(ORMModel):
    id: int
    employe_id: int
    admin_id: int
    type: TypePointage
    timestamp: datetime
    created_at: datetime


# ---------------------------------------------------------------- avertissement
class AvertissementCreate(BaseModel):
    pointage_id: Optional[int] = None
    employe_id: int
    type: TypeAvertissement
    date_concernee: datetime
    motif: Optional[str] = Field(None, max_length=100)


class AvertissementLift(BaseModel):
    lifted_reason: str = Field(..., max_length=255)


class AvertissementRead(ORMModel):
    id: int
    pointage_id: Optional[int] = None
    employe_id: int
    type: TypeAvertissement
    date_concernee: datetime
    motif: Optional[str] = None
    statut: StatutAvertissement
    created_at: datetime
    lifted_at: Optional[datetime] = None
    lifted_by: Optional[int] = None
    lifted_reason: Optional[str] = None


# ---------------------------------------------------------------- log
class LogCreate(BaseModel):
    user_id: Optional[int] = None
    action: str = Field(..., max_length=100)
    table_name: Optional[str] = Field(None, max_length=100)
    record_id: Optional[int] = None
    details: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)


class LogRead(LogCreate, ORMModel):
    id: int
    timestamp: datetime