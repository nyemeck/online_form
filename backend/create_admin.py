"""
Script utilitaire pour creer un administrateur.

Usage :
    python create_admin.py <username> <password>

Exemples :
    python create_admin.py bitjoka mon_mot_de_passe
    python create_admin.py mfopain autre_mot_de_passe
"""
import sys
from database import engine, SessionLocal
from models import Base, Admin
from auth import hash_password


def create_admin(username: str, password: str):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.username == username).first()
        if existing:
            print(f"Erreur : l'administrateur '{username}' existe deja.")
            sys.exit(1)

        admin = Admin(
            username=username,
            password_hash=hash_password(password),
        )
        db.add(admin)
        db.commit()
        print(f"Administrateur '{username}' cree avec succes.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python create_admin.py <username> <password>")
        sys.exit(1)

    create_admin(sys.argv[1], sys.argv[2])
