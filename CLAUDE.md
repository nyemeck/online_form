# Project: Academic Research Form — University of Ngaoundere

## Research Context
- **Researcher**: Prof. Laurent BITJOKA
- **Program**: Master in Public Organisation Management (ISMP Yaounde)
- **Supervisor**: Prof. MFOPAIN ABOUBAKAR (Dept. Management, Strategy & Foresight — FSEG, UN)
- **Subject**: Organisational and managerial innovation and performance of the University of Ngaoundere
- **Mandate**: Issued by the Rector of the University of Ngaoundere

## Questionnaire (42 items)
- **Section A**: General information (Gender, Status — 7 categories including public/private sector employers)
- **Section B**: Organisational innovation (IO1-IO5) — Likert 1-5
- **Section C**: Managerial innovation (IM1-IM5) — Likert 1-5
- **Section D**: University governance (G1-G5) — Likert 1-5
- **Section E**: Stakeholder engagement (E1-E5) — Likert 1-5
- **Section F**: Organisational learning capacity (A1-A5) — Likert 1-5
- **Section G**: University performance (public value approach)
  - G1: Academic performance (PA1-PA4) — Likert 1-5
  - G2: Organisational performance (PO1-PO4) — Likert 1-5
  - G3: Societal and developmental performance (PS1-PS4) — Likert 1-5
  - G4: Institutional performance / legitimacy (PI1-PI4) — Likert 1-5
- **Final comment**: Free text (optional)

## Tech Stack
- **Frontend**: HTML/CSS/JS (lightweight, compatible with limited connectivity in Cameroon)
- **Backend**: Python + FastAPI
- **Database**: SQLite
- **Export**: CSV/Excel for analysis (SPSS, pandas, etc.)
- **Hosting**: Hostinger VPS

## Project Structure
```
online_form/
├── CLAUDE.md                # Project context for Claude Code
├── backend/
│   ├── main.py              # FastAPI server
│   ├── database.py          # SQLite connection via SQLAlchemy
│   ├── models.py            # Pydantic models
│   ├── auth.py              # Admin authentication (JWT)
│   ├── logging_config.py    # Centralized logging configuration
│   ├── manage_admin.py      # CLI script for admin management (list, create, passwd, delete)
│   ├── .env                 # Environment variables (SECRET_KEY, LOG_LEVEL)
│   └── requirements.txt     # Python dependencies
├── docs/
│   ├── INFRASTRUCTURE.md    # VPS infrastructure (OS, Docker, Traefik, network, SSH keys)
│   ├── DEPLOYMENT.md        # Step-by-step deployment guide with commands
│   ├── RUNBOOK.md           # Operational procedures (systemd, logs, updates, admins)
│   ├── TODO.md              # Persistent task list (priority + details)
│   ├── SECURITY.md          # Backend security measures documentation
│   ├── SECURITY-TODO.md     # Security improvement backlog (priority + details)
│   ├── Questionnaire 3.pdf  # Original research questionnaire
│   └── BITJOKA_Mandat de recherche UN-ISMP.pdf  # Official Rector mandate
├── frontend/
│   ├── index.html           # Public form
│   ├── dashboard.html       # Admin dashboard (protected)
│   ├── login.html           # Admin login page
│   ├── assets/              # Images (logo, favicon) and SVG icons
│   ├── css/style.css        # Styles
│   └── js/
│       ├── app.js           # Form logic
│       └── dashboard.js     # Dashboard logic
├── scripts/
│   └── backup.sh            # Daily database backup script (cron)
└── exports/                 # Generated CSV/Excel files
```

## Python Dependencies
- fastapi, uvicorn — API and web server
- sqlalchemy — ORM for SQLite
- openpyxl — Excel export
- python-jose[cryptography] — JWT tokens (admin auth)
- passlib[bcrypt] — Password hashing
- python-multipart — Login form processing
- python-dotenv — Environment variables (.env)
- slowapi — Rate limiting

## Design Decisions
- Guaranteed anonymity (no IP or identifier collection)
- Password-protected admin access for dashboard and exports
- Real-time dashboard for tracking responses by respondent category

## Work Preferences
- Present each step with its context and rationale
- Wait for user validation before proceeding
- NEVER add "Co-Authored-By" in git commit messages
- All user-facing text must be in the translation files
  (`frontend/lang/fr.json` and `frontend/lang/en.json`). Never hardcode text
  visible to the user directly in HTML, JS, or API responses.
- For every new feature or backend endpoint, add relevant logs
  via the centralized logging system (`backend/logging_config.py`).
  Levels to use:
    - INFO: successful actions (create, update, export, etc.)
    - WARNING: non-blocking failures (invalid auth, validation failure)
    - ERROR: exceptions and system errors (with `exc_info=True`)
  NEVER log: passwords, JWT tokens, or sensitive personal data.
- On every security change, addition, or configuration update,
  update `docs/SECURITY.md` to document the implemented measure.
- All documentation files (.md) must be written in English.
