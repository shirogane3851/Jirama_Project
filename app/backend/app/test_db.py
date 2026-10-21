from sqlalchemy import text
from database import engine
from models import Employe

try:
    with engine.connect() as connexion:
        resultat = connexion.execute(text("SELECT version()"))
        print("Connexion PostgreSQL réussie !")
        print(resultat.scalar())

except Exception as erreur:
    print("Erreur de connexion :", erreur)
    

print("Modèle chargé :", Employe.__tablename__)