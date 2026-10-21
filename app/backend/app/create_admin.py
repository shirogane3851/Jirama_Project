"""Crée le premier employé + compte ADMIN_COMPTES.

Usage : python create_admin.py
(nécessaire car toutes les routes de création de comptes exigent déjà un admin)
"""
import getpass

from database import SessionLocal
from models import Compte, Employe, RoleEnum
from security import hash_password


def main() -> None:
    nom = input("Nom : ").strip()
    prenom = input("Prénom : ").strip()
    matricule = input("Matricule : ").strip()
    username = input("Nom d'utilisateur : ").strip()
    password = getpass.getpass("Mot de passe (8 caractères min.) : ")
    if len(password) < 8:
        raise SystemExit("Mot de passe trop court.")

    with SessionLocal() as db:
        employe = Employe(nom=nom, prenom=prenom, matricule=matricule)
        db.add(employe)
        db.flush()
        db.add(
            Compte(
                username=username,
                employe_id=employe.id,
                password_hash=hash_password(password),
                role=RoleEnum.ADMIN_COMPTES,
            )
        )
        db.commit()
    print("Compte admin créé.")


if __name__ == "__main__":
    main()
