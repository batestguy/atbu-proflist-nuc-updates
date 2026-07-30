"""
database.py — SQLAlchemy models + database initialization
ATBU Academic Planning Portal — Phase 1 Foundation

Schema design:
- professors: Main table with composite UNIQUE key (last_name, first_name, department)
- phone_numbers: Separate table for multiple phones per professor
- app_settings: Key-value store for password hash, faculty normalization, config
- import_history: Log of every Excel import operation

The composite UNIQUE key enables UPDATE-on-import: when re-importing data,
matching records are updated rather than duplicated.
"""

import os
import sys
import json
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, 
    ForeignKey, TIMESTAMP, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# ---------------------------------------------------------------------------
# Paths — handle both development and PyInstaller .exe mode
# ---------------------------------------------------------------------------
def _get_data_dir():
    """
    Return the directory for persistent data files.
    For portable distribution (self-contained folder):
      1. Look for existing data/ in PARENT directory first (dev mode with real data)
      2. If not found, look next to the .exe or script (portable/distribution mode)
      3. Create data/ next to the .exe or script
    This ensures real data is always found first (the dist/data/ empty DB is skipped).
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller .exe mode
        base = os.path.dirname(sys.executable)
    else:
        # Development / script mode
        base = os.path.dirname(os.path.abspath(__file__))
    
    # Check 1: data/ in parent directory (dev mode with real data)
    parent_dir = os.path.dirname(base)
    parent_data = os.path.join(parent_dir, "data")
    parent_db = os.path.join(parent_data, "professors.db")
    if os.path.isfile(parent_db):
        return parent_data
    
    # Check 2: data/ next to .exe or script (portable / distribution mode)
    data_dir = os.path.join(base, "data")
    db_path = os.path.join(data_dir, "professors.db")
    if os.path.isfile(db_path):
        return data_dir
    
    # Fallback: create data/ next to .exe or script
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

DB_DIR = _get_data_dir()
DB_PATH = os.path.join(DB_DIR, "professors.db")
os.makedirs(DB_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# SQLAlchemy Setup
# ---------------------------------------------------------------------------
engine = create_engine(
    f"sqlite:///{DB_PATH}", echo=False,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False)


# ============================================================================
# MODELS
# ============================================================================

class Professor(Base):
    """
    Main professors table.
    Composite UNIQUE key: (last_name, first_name, department)
    This prevents exact duplicates and drives the UPDATE-on-import strategy.
    """
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ---- NUC Fields ----
    last_name = Column(String(100), nullable=False, index=True)
    first_name = Column(String(100), nullable=False, index=True)
    other_names = Column(String(200), nullable=True)
    date_of_professorship = Column(String(20), nullable=False)  # YYYY-MM-DD
    faculty = Column(String(200), nullable=False, index=True)
    department = Column(String(200), nullable=False, index=True)
    area_of_specialization = Column(String(300), nullable=False, index=True)
    email = Column(String(200), nullable=True)

    # ---- Additional Fields ----
    sex = Column(String(10), nullable=True)           # M / F
    rank = Column(String(50), nullable=True, default="Professor")
    is_retired = Column(Integer, nullable=False, default=0)
    retirement_date = Column(String(20), nullable=True)
    retirement_status = Column(String(50), nullable=True)  # Retirement, Death, Transfer of Service
    added_year = Column(Integer, nullable=True)
    source_file = Column(String(300), nullable=True)
    notes = Column(Text, nullable=True)

    # ---- Metadata ----
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # ---- Relationships ----
    phone_numbers = relationship(
        "PhoneNumber", back_populates="professor",
        cascade="all, delete-orphan", lazy="selectin"
    )

    # ---- Constraints ----
    __table_args__ = (
        UniqueConstraint(
            "last_name", "first_name", "department",
            name="uq_professor_name_dept"
        ),
        Index("idx_professors_specialization", "area_of_specialization"),
        Index("idx_professors_name", "last_name", "first_name"),
    )

    def to_dict(self, include_phones=True):
        """Serialize professor to dictionary (for export, display, JSON)."""
        data = {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "other_names": self.other_names or "",
            "date_of_professorship": self.date_of_professorship,
            "faculty": self.faculty,
            "department": self.department,
            "area_of_specialization": self.area_of_specialization,
            "email": self.email or "",
            "sex": self.sex or "",
            "rank": self.rank or "Professor",
            "is_retired": bool(self.is_retired),
            "retirement_date": self.retirement_date or "",
            "retirement_status": self.retirement_status or "",
            "added_year": self.added_year,
            "source_file": self.source_file or "",
        }
        if include_phones:
            data["phone_numbers"] = [pn.phone for pn in self.phone_numbers]
        return data

    def __repr__(self):
        return f"<Professor {self.last_name}, {self.first_name} — {self.department}>"


class PhoneNumber(Base):
    """
    Separate phone numbers table — supports MULTIPLE phones per professor.
    The NUC format has a single phone field, but real data sometimes has
    multiple numbers delimited by '/'. We split these on import.
    On export, they are rejoined with ' / '.
    """
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    professor_id = Column(Integer, ForeignKey("professors.id", ondelete="CASCADE"), nullable=False)
    phone = Column(String(50), nullable=False)
    is_primary = Column(Integer, default=0)

    professor = relationship("Professor", back_populates="phone_numbers")

    def __repr__(self):
        return f"<Phone {self.phone} (primary={self.is_primary})>"


class AppSetting(Base):
    """
    Key-value store for application settings.
    Keys:
      - password_hash: bcrypt hash of the admin password
      - db_version: schema version for migrations
      - faculty_normalization: JSON mapping of faculty name corrections
      - auto_lock_minutes: inactivity timeout for edit mode
    """
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Setting {self.key}>"


class ImportHistory(Base):
    """
    Log of every Excel import operation.
    Tracks how many records were added, updated, or skipped.
    """
    __tablename__ = "import_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(300), nullable=False)
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    imported_at = Column(TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f"<Import {self.filename}: +{self.records_added} ~{self.records_updated} -{self.records_skipped}>"


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_db(echo=False):
    """
    Create all tables in the SQLite database.
    Safe to call multiple times — uses IF NOT EXISTS internally.
    
    Args:
        echo: If True, prints SQL statements (useful for debugging).
    
    Returns:
        The SQLAlchemy engine instance.
    """
    from sqlalchemy import inspect as sa_inspect
    inspector = sa_inspect(engine)
    if 'professors' in inspector.get_table_names():
        # Tables already exist — skip create_all, just ensure defaults
        session = SessionLocal()
        try:
            _ensure_defaults(session)
        finally:
            session.close()
        return engine
    Base.metadata.create_all(engine)
    
    # Insert default settings if they don't exist
    session = SessionLocal()
    try:
        _ensure_defaults(session)
    finally:
        session.close()
    
    return engine


def _ensure_defaults(session):
    """Insert default app_settings if they don't exist."""
    defaults = {
        "db_version": "1",
        "auto_lock_minutes": "15",
        "faculty_normalization": json.dumps({
            # Discovered from actual data scan — inconsistencies to normalize
            "Environmental Technoloty": "Environmental Technology",
            "College of Medical Science": "College of Medical Sciences",
            "Management Science": "Management Sciences",
            "Engineering and Engineering technology": "Engineering and Engineering Technology",
        }),
    }
    for key, value in defaults.items():
        existing = session.query(AppSetting).filter_by(key=key).first()
        if not existing:
            session.add(AppSetting(key=key, value=value))
    session.commit()


def get_session():
    """Get a new database session."""
    return SessionLocal()
