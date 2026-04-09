# Projet : Formulaire de recherche académique - Université de Ngaoundere

## Contexte de la recherche
- **Chercheur** : Prof. Laurent BITJOKA
- **Formation** : Master Professionnel en Management des Organisations Publiques (ISMP Yaounde)
- **Encadrant** : Prof. MFOPAIN ABOUBAKAR (Dept. Management, Strategie et Prospective - FSEG, UN)
- **Sujet** : Innovation organisationnelle et manageriale et performance de l'Universite de Ngaoundere
- **Mandat** : Delivre par le Recteur de l'Universite de Ngaoundere

## Questionnaire (42 items)
- **Section A** : Informations generales (Sexe, Statut -- 7 categories dont Employeur secteur public et prive)
- **Section B** : Innovation organisationnelle (IO1-IO5) -- Likert 1-5
- **Section C** : Innovation manageriale (IM1-IM5) -- Likert 1-5
- **Section D** : Gouvernance universitaire (G1-G5) -- Likert 1-5
- **Section E** : Engagement des acteurs (E1-E5) -- Likert 1-5
- **Section F** : Capacite d'apprentissage organisationnel (A1-A5) -- Likert 1-5
- **Section G** : Performance universitaire (approche valeur publique)
  - G1 : Performance academique (PA1-PA4) -- Likert 1-5
  - G2 : Performance organisationnelle (PO1-PO4) -- Likert 1-5
  - G3 : Performance societale et developpementale (PS1-PS4) -- Likert 1-5
  - G4 : Performance institutionnelle / legitimite (PI1-PI4) -- Likert 1-5
- **Remarque finale** : Texte libre (optionnel)

## Stack technique
- **Frontend** : HTML/CSS/JS (leger, compatible connexion limitee Cameroun)
- **Backend** : Python + FastAPI
- **Base de donnees** : SQLite
- **Export** : CSV/Excel pour analyse (SPSS, pandas, etc.)
- **Hebergement** : VPS Hostinger

## Architecture du projet
```
online_form/
├── CLAUDE.md                # Contexte du projet pour Claude Code
├── backend/
│   ├── main.py              # Serveur API FastAPI
│   ├── database.py          # Connexion SQLite via SQLAlchemy
│   ├── models.py            # Modeles Pydantic
│   ├── auth.py              # Authentification admin (JWT)
│   ├── manage_admin.py      # Script CLI gestion admins (list, create, passwd, delete)
│   ├── .env                 # Variables d'environnement (SECRET_KEY, ADMIN_PASSWORD)
│   └── requirements.txt     # Dependances Python
├── docs/
│   ├── INFRASTRUCTURE.md    # Infrastructure VPS (OS, Docker, Traefik, reseau, cles SSH)
│   ├── DEPLOYMENT.md        # Guide de deploiement etape par etape avec commandes
│   ├── RUNBOOK.md           # Procedures operationnelles (systemd, logs, mises a jour, admins)
│   ├── TODO.md              # Liste persistante des taches a faire (priorite + details)
│   ├── Questionnaire 3.pdf  # Questionnaire original de la recherche
│   └── BITJOKA_Mandat de recherche UN-ISMP.pdf  # Mandat officiel du Recteur
├── frontend/
│   ├── index.html           # Formulaire public
│   ├── dashboard.html       # Tableau de bord admin (protege)
│   ├── login.html           # Page connexion admin
│   ├── assets/              # Images : logo.png, favicon.png
│   ├── css/style.css        # Styles
│   └── js/
│       ├── app.js           # Logique formulaire
│       └── dashboard.js     # Logique dashboard
└── exports/                 # Fichiers CSV/Excel exportes
```

## Dependances Python
- fastapi, uvicorn — API et serveur web
- sqlalchemy — ORM pour SQLite
- openpyxl — Export Excel
- python-jose[cryptography] — Tokens JWT (auth admin)
- passlib[bcrypt] — Hashage mot de passe
- python-multipart — Traitement formulaires login
- python-dotenv — Variables d'environnement (.env)

## Decisions prises
- Anonymat garanti (pas de collecte IP/identifiants)
- Acces admin protege par mot de passe pour dashboard et exports
- Dashboard temps reel pour suivi de collecte par categorie de repondant

## Preferences de travail
- Presenter chaque etape avec son contexte et sa necessite
- Attendre la validation de l'utilisateur avant de continuer
- Ne JAMAIS ajouter "Co-Authored-By" dans les messages de commit
