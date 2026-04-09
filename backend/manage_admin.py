"""
Script de gestion des administrateurs.

Usage:
    python3 manage_admin.py list                 # Lister les admins
    python3 manage_admin.py create <username>    # Creer un admin
    python3 manage_admin.py passwd <username>    # Changer le mot de passe
    python3 manage_admin.py delete <username>    # Supprimer un admin
"""

import sys
import getpass
import logging

from database import engine, Base
from models import Admin
from auth import hash_password
from logging_config import setup_logging
from sqlalchemy.orm import Session

setup_logging()
logger = logging.getLogger("manage_admin")


def list_admins():
    with Session(engine) as db:
        admins = db.query(Admin).order_by(Admin.id).all()
        if not admins:
            print("Aucun administrateur enregistre.")
            return
        print(f"{'ID':<6} {'Username'}")
        print("-" * 30)
        for a in admins:
            print(f"{a.id:<6} {a.username}")
        print(f"\nTotal : {len(admins)} admin(s)")


def prompt_password():
    try:
        while True:
            password = getpass.getpass("Mot de passe : ")
            if len(password) < 8:
                print("Le mot de passe doit contenir au moins 8 caracteres.")
                continue
            confirm = getpass.getpass("Confirmer le mot de passe : ")
            if password != confirm:
                print("Les mots de passe ne correspondent pas.")
                continue
            return password
    except KeyboardInterrupt:
        print("\nOperation annulee.")
        sys.exit(0)


def create_admin(username):
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        existing = db.query(Admin).filter(Admin.username == username).first()
        if existing:
            print(f"Erreur : l'admin '{username}' existe deja.")
            sys.exit(1)
        password = prompt_password()
        admin = Admin(username=username, password_hash=hash_password(password))
        db.add(admin)
        db.commit()
        logger.info(f"Admin created: user={username}")
        print(f"Admin '{username}' cree avec succes.")


def change_password(username):
    with Session(engine) as db:
        admin = db.query(Admin).filter(Admin.username == username).first()
        if not admin:
            print(f"Erreur : l'admin '{username}' n'existe pas.")
            sys.exit(1)
        password = prompt_password()
        admin.password_hash = hash_password(password)
        db.commit()
        logger.info(f"Admin password changed: user={username}")
        print(f"Mot de passe de '{username}' mis a jour.")


def delete_admin(username):
    with Session(engine) as db:
        admin = db.query(Admin).filter(Admin.username == username).first()
        if not admin:
            print(f"Erreur : l'admin '{username}' n'existe pas.")
            sys.exit(1)
        confirm = input(f"Supprimer l'admin '{username}' ? (oui/non) : ")
        if confirm.lower() != "oui":
            print("Suppression annulee.")
            return
        db.delete(admin)
        db.commit()
        logger.info(f"Admin deleted: user={username}")
        print(f"Admin '{username}' supprime.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_admins()
    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage : python3 manage_admin.py create <username>")
            sys.exit(1)
        create_admin(sys.argv[2])
    elif command == "passwd":
        if len(sys.argv) < 3:
            print("Usage : python3 manage_admin.py passwd <username>")
            sys.exit(1)
        change_password(sys.argv[2])
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage : python3 manage_admin.py delete <username>")
            sys.exit(1)
        delete_admin(sys.argv[2])
    else:
        print(f"Commande inconnue : {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
