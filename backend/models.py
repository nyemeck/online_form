from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)


class Response(Base):
    __tablename__ = "responses"

    # Technical columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Form language (fr, en, etc.)
    language = Column(String, nullable=False)

    # Section A - General information
    gender = Column(String, nullable=False)
    status = Column(String, nullable=False)

    # Section B - Organisational innovation
    io1 = Column(Integer, nullable=False)
    io2 = Column(Integer, nullable=False)
    io3 = Column(Integer, nullable=False)
    io4 = Column(Integer, nullable=False)
    io5 = Column(Integer, nullable=False)

    # Section C - Managerial innovation
    im1 = Column(Integer, nullable=False)
    im2 = Column(Integer, nullable=False)
    im3 = Column(Integer, nullable=False)
    im4 = Column(Integer, nullable=False)
    im5 = Column(Integer, nullable=False)

    # Section D - University governance
    g1 = Column(Integer, nullable=False)
    g2 = Column(Integer, nullable=False)
    g3 = Column(Integer, nullable=False)
    g4 = Column(Integer, nullable=False)
    g5 = Column(Integer, nullable=False)

    # Section E - Stakeholder engagement
    e1 = Column(Integer, nullable=False)
    e2 = Column(Integer, nullable=False)
    e3 = Column(Integer, nullable=False)
    e4 = Column(Integer, nullable=False)
    e5 = Column(Integer, nullable=False)

    # Section F - Organisational learning capacity
    a1 = Column(Integer, nullable=False)
    a2 = Column(Integer, nullable=False)
    a3 = Column(Integer, nullable=False)
    a4 = Column(Integer, nullable=False)
    a5 = Column(Integer, nullable=False)

    # Section G1 - Academic performance
    pa1 = Column(Integer, nullable=False)
    pa2 = Column(Integer, nullable=False)
    pa3 = Column(Integer, nullable=False)
    pa4 = Column(Integer, nullable=False)

    # Section G2 - Organisational performance
    po1 = Column(Integer, nullable=False)
    po2 = Column(Integer, nullable=False)
    po3 = Column(Integer, nullable=False)
    po4 = Column(Integer, nullable=False)

    # Section G3 - Societal and developmental performance
    ps1 = Column(Integer, nullable=False)
    ps2 = Column(Integer, nullable=False)
    ps3 = Column(Integer, nullable=False)
    ps4 = Column(Integer, nullable=False)

    # Section G4 - Institutional performance (legitimacy)
    pi1 = Column(Integer, nullable=False)
    pi2 = Column(Integer, nullable=False)
    pi3 = Column(Integer, nullable=False)
    pi4 = Column(Integer, nullable=False)

    # Final comment (optional)
    comment = Column(Text, nullable=True)
