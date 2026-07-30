"""
run_import.py — Phase 1: Initialize DB + Import both Excel files + Verify
Run with: D:\\appdev-env\\Scripts\\python.exe run_import.py
"""

import os
import sys
import json
from datetime import datetime

# Add project dir to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from database import init_db, get_session, Professor, PhoneNumber, AppSetting, ImportHistory
from import_export import import_excel, export_nuc_format

# Paths
EXCEL_DIR = r"D:\Apps for ATBU"
NUC_FILE = os.path.join(EXCEL_DIR, "2.NUC FORMAT_FOR_FULL_PROFESSORS_LIST AUGUST 2025.xlsx")
NEWLY_FILE = os.path.join(EXCEL_DIR, "Newly Promoted Professors 2024 to date.xlsx")
DB_PATH = os.path.join(project_dir, "data", "professors.db")
EXPORT_PATH = os.path.join(project_dir, "data", "export_nuc_format.xlsx")

print("=" * 60)
print("ATBU ACADEMIC PLANNING PORTAL — Phase 1 Import")
print("=" * 60)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Step 1: Initialize database
print("[1/5] Initializing database...")
engine = init_db(echo=False)
print(f"       Database: {DB_PATH}")
print(f"       Tables created: professors, phone_numbers, app_settings, import_history")
print()

# Step 2: Import NUC format
print("[2/5] Importing NUC format...")
print(f"       File: {NUC_FILE}")
if os.path.exists(NUC_FILE):
    result_nuc = import_excel(NUC_FILE)
    print(f"       Added: {result_nuc['added']} | Updated: {result_nuc['updated']} | Skipped: {result_nuc['skipped']} | Total: {result_nuc['total']}")
else:
    print(f"       ⚠️ File not found: {NUC_FILE}")
    result_nuc = {"added": 0, "updated": 0, "skipped": 0, "total": 0}
print()

# Step 3: Import Newly Promoted format
print("[3/5] Importing Newly Promoted format...")
print(f"       File: {NEWLY_FILE}")
if os.path.exists(NEWLY_FILE):
    result_newly = import_excel(NEWLY_FILE)
    print(f"       Added: {result_newly['added']} | Updated: {result_newly['updated']} | Skipped: {result_newly['skipped']} | Total: {result_newly['total']}")
else:
    print(f"       ⚠️ File not found: {NEWLY_FILE}")
    result_newly = {"added": 0, "updated": 0, "skipped": 0, "total": 0}
print()

# Step 4: Verification queries
print("[4/5] Verification queries...")
session = get_session()

total_profs = session.query(Professor).count()
active_profs = session.query(Professor).filter_by(is_retired=0).count()
total_phones = session.query(PhoneNumber).count()
total_imports = session.query(ImportHistory).count()

print(f"       Total professors: {total_profs}")
print(f"       Active professors: {active_profs}")
print(f"       Total phone numbers: {total_phones}")
print(f"       Total import history entries: {total_imports}")

# Faculty breakdown
print(f"\n       --- Faculties ---")
faculties = session.query(Professor.faculty).distinct().order_by(Professor.faculty).all()
for (faculty,) in faculties:
    if faculty:
        count = session.query(Professor).filter_by(faculty=faculty).count()
        print(f"       {faculty}: {count} professors")

# Department breakdown
print(f"\n       --- Top 10 Departments ---")
depts = (
    session.query(Professor.department)
    .group_by(Professor.department)
    .order_by(Professor.department)
    .all()
)
for (dept,) in depts[:10]:
    if dept:
        count = session.query(Professor).filter_by(department=dept).count()
        print(f"       {dept}: {count}")

# Phone stats
multi_phone = session.query(Professor.id).filter(
    Professor.id.in_(
        session.query(PhoneNumber.professor_id)
        .group_by(PhoneNumber.professor_id)
        .having(PhoneNumber.professor_id > 0)
    )
).count()
print(f"       Professors with phone numbers: {multi_phone}")

# Sample professors
print(f"\n       --- Sample Professors (first 5) ---")
samples = session.query(Professor).limit(5).all()
for s in samples:
    phones = " / ".join(pn.phone for pn in s.phone_numbers)
    print(f"       {s.last_name}, {s.first_name} ({s.department}) — {phones}")

session.close()
print()

# Step 5: Export test
print("[5/5] Testing NUC export...")
try:
    count = export_nuc_format(EXPORT_PATH)
    print(f"       Exported {count} professors to: {EXPORT_PATH}")
except Exception as e:
    print(f"       ⚠️ Export failed: {e}")

print()
print("=" * 60)
print("PHASE 1 COMPLETE")
print("=" * 60)
