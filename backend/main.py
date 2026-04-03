from enum import Enum
from typing import Optional
from datetime import datetime
import csv
import io
import os

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from openpyxl import Workbook

from database import engine, get_db, Base
from models import Response
from auth import authenticate_admin, create_access_token, get_current_admin

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Research Form - University of Ngaoundere")

# --- Validation enums ---

class GenderEnum(str, Enum):
    M = "M"       # Masculin / Male
    F = "F"       # Feminin / Female
    NR = "NR"     # Prefer not to say


class StatusEnum(str, Enum):
    EC = "EC"     # Lecturer-researcher
    PA = "PA"     # Administrative staff
    RA = "RA"     # Academic / administrative leader
    ET = "ET"     # Student
    GOV = "GOV"   # Government (MINESUP, MINFI)
    EPU = "EPU"   # Public sector employer
    EPR = "EPR"   # Private sector employer


class LanguageEnum(str, Enum):
    FR = "fr"
    EN = "en"


# --- Pydantic schema for form submission ---

class ResponseCreate(BaseModel):
    # Form language
    language: LanguageEnum

    # Section A - General information
    gender: GenderEnum
    status: StatusEnum

    # Section B - Organisational innovation
    io1: int = Field(ge=1, le=5)
    io2: int = Field(ge=1, le=5)
    io3: int = Field(ge=1, le=5)
    io4: int = Field(ge=1, le=5)
    io5: int = Field(ge=1, le=5)

    # Section C - Managerial innovation
    im1: int = Field(ge=1, le=5)
    im2: int = Field(ge=1, le=5)
    im3: int = Field(ge=1, le=5)
    im4: int = Field(ge=1, le=5)
    im5: int = Field(ge=1, le=5)

    # Section D - University governance
    g1: int = Field(ge=1, le=5)
    g2: int = Field(ge=1, le=5)
    g3: int = Field(ge=1, le=5)
    g4: int = Field(ge=1, le=5)
    g5: int = Field(ge=1, le=5)

    # Section E - Stakeholder engagement
    e1: int = Field(ge=1, le=5)
    e2: int = Field(ge=1, le=5)
    e3: int = Field(ge=1, le=5)
    e4: int = Field(ge=1, le=5)
    e5: int = Field(ge=1, le=5)

    # Section F - Organisational learning capacity
    a1: int = Field(ge=1, le=5)
    a2: int = Field(ge=1, le=5)
    a3: int = Field(ge=1, le=5)
    a4: int = Field(ge=1, le=5)
    a5: int = Field(ge=1, le=5)

    # Section G1 - Academic performance
    pa1: int = Field(ge=1, le=5)
    pa2: int = Field(ge=1, le=5)
    pa3: int = Field(ge=1, le=5)
    pa4: int = Field(ge=1, le=5)

    # Section G2 - Organisational performance
    po1: int = Field(ge=1, le=5)
    po2: int = Field(ge=1, le=5)
    po3: int = Field(ge=1, le=5)
    po4: int = Field(ge=1, le=5)

    # Section G3 - Societal performance
    ps1: int = Field(ge=1, le=5)
    ps2: int = Field(ge=1, le=5)
    ps3: int = Field(ge=1, le=5)
    ps4: int = Field(ge=1, le=5)

    # Section G4 - Institutional performance
    pi1: int = Field(ge=1, le=5)
    pi2: int = Field(ge=1, le=5)
    pi3: int = Field(ge=1, le=5)
    pi4: int = Field(ge=1, le=5)

    # Final comment
    comment: Optional[str] = None


# --- Public endpoints ---

@app.post("/api/responses", status_code=status.HTTP_201_CREATED)
def submit_response(data: ResponseCreate, db: Session = Depends(get_db)):
    response = Response(**data.model_dump())
    db.add(response)
    db.commit()
    return {"message": "Response recorded successfully"}


@app.post("/api/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = authenticate_admin(form.username, form.password, db)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(admin.username)
    return {"access_token": token, "token_type": "bearer"}


# --- Protected endpoints (admin) ---

@app.get("/api/stats")
def get_stats(admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    total = db.query(Response).count()

    gender_stats = {}
    for gender in GenderEnum:
        count = db.query(Response).filter(Response.gender == gender.value).count()
        gender_stats[gender.value] = count

    status_stats = {}
    for status_val in StatusEnum:
        count = db.query(Response).filter(Response.status == status_val.value).count()
        status_stats[status_val.value] = count

    language_stats = {}
    for lang in LanguageEnum:
        count = db.query(Response).filter(Response.language == lang.value).count()
        language_stats[lang.value] = count

    return {
        "total": total,
        "by_gender": gender_stats,
        "by_status": status_stats,
        "by_language": language_stats,
    }


# Export columns
EXPORT_COLUMNS = [
    "id", "created_at", "language", "gender", "status",
    "io1", "io2", "io3", "io4", "io5",
    "im1", "im2", "im3", "im4", "im5",
    "g1", "g2", "g3", "g4", "g5",
    "e1", "e2", "e3", "e4", "e5",
    "a1", "a2", "a3", "a4", "a5",
    "pa1", "pa2", "pa3", "pa4",
    "po1", "po2", "po3", "po4",
    "ps1", "ps2", "ps3", "ps4",
    "pi1", "pi2", "pi3", "pi4",
    "comment",
]


def get_all_responses(db: Session) -> list[dict]:
    responses = db.query(Response).order_by(Response.id).all()
    rows = []
    for r in responses:
        row = {}
        for col in EXPORT_COLUMNS:
            value = getattr(r, col)
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            row[col] = value
        rows.append(row)
    return rows


@app.get("/api/export/csv")
def export_csv(admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = get_all_responses(db)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=responses.csv"},
    )


@app.get("/api/export/excel")
def export_excel(admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = get_all_responses(db)
    wb = Workbook()
    ws = wb.active
    ws.title = "Responses"
    ws.append(EXPORT_COLUMNS)
    for row in rows:
        ws.append([row[col] for col in EXPORT_COLUMNS])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=responses.xlsx"},
    )


# --- Serve frontend ---

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

@app.get("/")
def serve_form():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/login")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/dashboard")
def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
