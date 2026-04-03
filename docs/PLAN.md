# Plan de developpement - Formulaire de recherche UN

## Etat d'avancement

### Etape 1 : Structure du projet [FAIT]
- Creation des dossiers (backend/, frontend/, docs/, exports/)
- Deplacement des documents de reference dans docs/
- Initialisation git + .gitignore

### Etape 2 : Dependances Python [FAIT]
- requirements.txt avec 8 librairies (FastAPI, SQLAlchemy, JWT, etc.)

### Etape 3 : Connexion base de donnees [FAIT]
- database.py : moteur SQLAlchemy, session, connexion SQLite (responses.db)

### Etape 4 : Modele de donnees [FAIT]
- models.py : table responses (44 colonnes = 2 techniques + 42 items)
- Sexe/Statut en String avec validation Enum prevue dans main.py

### Etape 5 : Authentification admin [FAIT]
- auth.py : hashage bcrypt, verification via BDD, token JWT 24h
- .env.example : modele pour SECRET_KEY uniquement

### Etape 5b : Gestion multi-admins [FAIT]
- Modele Admin dans models.py (table admins : id, username, password_hash)
- create_admin.py : script utilitaire pour ajouter un admin en ligne de commande

---

### Etape 6 : Serveur API principal [FAIT]
- main.py : endpoints FastAPI
  - POST /api/responses : recevoir une soumission du formulaire
  - POST /api/login : connexion admin
  - GET /api/stats : statistiques pour le dashboard (protege)
  - GET /api/export/csv : export CSV (protege)
  - GET /api/export/excel : export Excel (protege)
- Validation Enum avec codes i18n (M/F/NR, EC/PA/RA/ET/GOV/EPU/EPR)
- Schemas Pydantic avec validation Likert 1-5

### Etape 6b : Internationalisation (i18n) [FAIT]
- Approche par codes neutres cote backend (M, F, EC, PA, etc.)
- Dictionnaires de traduction : frontend/lang/fr.json et en.json
- Structure extensible (ajout d'une langue = ajout d'un fichier JSON)

### Etape 7 : Frontend - Formulaire public [A FAIRE]
- index.html : formulaire responsive avec toutes les sections A-G
- css/style.css : mise en forme professionnelle, adaptee mobile
- js/app.js : validation cote client, envoi des donnees, chargement i18n
- Selecteur de langue FR / EN

### Etape 8 : Frontend - Espace admin [A FAIRE]
- login.html : page de connexion admin
- dashboard.html : tableau de bord temps reel
  - Nombre total de reponses
  - Repartition par sexe et par statut
  - Graphiques de suivi
- js/dashboard.js : logique du dashboard, appels API

### Etape 9 : Export des donnees [A FAIRE]
- Export CSV et Excel depuis le dashboard
- Format compatible SPSS / Python pandas / Excel

### Etape 10 : Deploiement VPS Hostinger [A FAIRE]
- Guide de deploiement (nginx, systemd, SSL)
- Configuration du domaine
- Mise en production
