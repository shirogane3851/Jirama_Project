import io
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from database import get_db
from models import Compte, Employe, RoleEnum
from security import get_current_compte, require_roles
from utils import get_or_404, persist

router = APIRouter(prefix="/employes", tags=["Photos"])

PHOTO_DIR = Path(os.getenv("PHOTO_DIR", "/var/lib/jirama/photos"))
MAX_BYTES = 2 * 1024 * 1024          # taille maximale du fichier envoyé
SIDE = 512                           # côté maximal de la photo enregistrée
VIEW_ROLES = (RoleEnum.AGENT_POINTAGE, RoleEnum.VALIDATEUR_CONGE, RoleEnum.ADMIN_COMPTES)
Image.MAX_IMAGE_PIXELS = 25_000_000  # refuse les « bombes de décompression »


@router.post("/{employe_id}/photo", status_code=204)
async def upload_photo(
    employe_id: int,
    request: Request,
    fichier: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(RoleEnum.ADMIN_COMPTES)),
):
    employe = get_or_404(db, Employe, employe_id, "Employé")
    data = await fichier.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Photo trop lourde (2 Mo maximum)")
    try:
        img = Image.open(io.BytesIO(data))
        if img.format not in ("JPEG", "PNG", "WEBP"):
            raise ValueError("format refusé")
        img = ImageOps.exif_transpose(img).convert("RGB")
    except (UnidentifiedImageError, ValueError, OSError, Image.DecompressionBombError):
        raise HTTPException(415, "Fichier non reconnu : envoyez une photo JPEG, PNG ou WebP")
    img.thumbnail((SIDE, SIDE))

    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    nom = f"{uuid.uuid4().hex}.jpg"
    chemin = PHOTO_DIR / nom
    img.save(chemin, "JPEG", quality=85, optimize=True)  # recompression : retire EXIF et contenu caché
    os.chmod(chemin, 0o640)

    ancien = employe.photo_identite
    employe.photo_identite = nom
    try:
        persist(db, request, current.id, "UPDATE", employe, "employe", "photo")
    except HTTPException:
        chemin.unlink(missing_ok=True)
        raise
    if ancien:
        (PHOTO_DIR / Path(ancien).name).unlink(missing_ok=True)


@router.get("/{employe_id}/photo")
def get_photo(
    employe_id: int,
    db: Session = Depends(get_db),
    current: Compte = Depends(get_current_compte),
):
    if current.role not in VIEW_ROLES and current.employe_id != employe_id:
        raise HTTPException(403, "Accès refusé")
    employe = get_or_404(db, Employe, employe_id, "Employé")
    if not employe.photo_identite:
        raise HTTPException(404, "Pas de photo")
    chemin = PHOTO_DIR / Path(employe.photo_identite).name  # .name empêche tout « ../ »
    if not chemin.is_file():
        raise HTTPException(404, "Photo introuvable")
    return FileResponse(
        chemin,
        media_type="image/jpeg",
        headers={"Cache-Control": "private, no-cache", "X-Content-Type-Options": "nosniff"},
    )


@router.delete("/{employe_id}/photo", status_code=204)
def delete_photo(
    employe_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current: Compte = Depends(require_roles(RoleEnum.ADMIN_COMPTES)),
):
    employe = get_or_404(db, Employe, employe_id, "Employé")
    ancien = employe.photo_identite
    employe.photo_identite = None
    persist(db, request, current.id, "UPDATE", employe, "employe", "photo retirée")
    if ancien:
        (PHOTO_DIR / Path(ancien).name).unlink(missing_ok=True)