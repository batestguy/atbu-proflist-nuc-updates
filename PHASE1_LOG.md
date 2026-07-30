# Phase 1 Implementation Log — Foundation Layer

> **Project:** ATBU Academic Planning Portal  
> **Phase:** 1 — Foundation (Database, Import, Export)  
> **Date:** 2026-07-27  
> **Status:** ✅ Complete

---

## 1. Project Structure

```
D:\Apps for ATBU\atbu_professors_app\
├── database.py           # SQLAlchemy models + DB init
├── name_parser.py        # Full name → components splitting
├── import_export.py      # Excel import/export logic
├── run_import.py         # Phase 1 test script (import both files)
├── screens/              # Flet UI screens (Phase 2)
├── assets/               # ATBU logo, director photo
├── data/
│   ├── professors.db     # SQLite database file
│   └── export_nuc_format.xlsx  # Sample export
└── PHASE1_LOG.md         # This file
```

---

## 2. Database Schema Design

### 2.1 Professors Table

The central table with a **composite UNIQUE constraint** on `(last_name, first_name, department)`:

```sql
UNIQUE(last_name, first_name, department)
```

**Why this key?**
- Based on actual data analysis: 172 NUC records + 57 Newly Promoted records
- Only 1 true duplicate found (same name + same department: "Abubakar Muhammad" in Animal Production ×2)
- The composite key catches duplicates on import and triggers UPDATE instead of INSERT
- Enables safe re-importing of the same Excel files without creating duplicates

### 2.2 Phone Numbers Table (Separate)

```sql
CREATE TABLE phone_numbers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    professor_id INTEGER NOT NULL,
    phone TEXT NOT NULL,
    is_primary INTEGER DEFAULT 0,
    FOREIGN KEY (professor_id) REFERENCES professors(id) ON DELETE CASCADE
);
```

**Why separate table?**
- Data analysis found 2 records with multiple phones (delimited by `/`)
- Spec requirement: "phone numbers could be multiple"
- Normalized design allows adding/removing individual numbers without modifying the main table
- On export, phones are joined with ` / ` delimiter to fit NUC format's single column

### 2.3 App Settings Table

Key-value store for:
- `password_hash` — bcrypt hash (set on first launch, Phase 2/3)
- `db_version` — schema migration tracking
- `faculty_normalization` — JSON mapping for faculty name fixes
- `auto_lock_minutes` — inactivity timeout for edit mode

### 2.4 Import History Table

Logs every Excel import: filename, records added/updated/skipped, timestamp.

### 2.5 Indexes Created

- `idx_professors_faculty` — fast faculty filtering
- `idx_professors_department` — fast department filtering
- `idx_professors_specialization` — fast specialization filtering
- `idx_professors_name` — fast name search
- `idx_phone_professor` — fast phone lookup by professor

---

## 3. Name Parser Design

### 3.1 Name Splitting Logic

```
"Bose Adamu Abdullahi" → last_name="Abdullahi", first_name="Bose", other_names="Adamu"
"Sale Idi"             → last_name="Idi", first_name="Sale", other_names=""
```

- **Last token** = Last Name (surname)
- **First token** = First Name (given name)
- **Middle tokens** = Other Names

### 3.2 Edge Cases Handled

| Edge Case | Handling |
|---|---|
| Single-word name | Treated as first name, last name empty |
| Suffixes (Jr., Sr., III) | Attached to last name: "Smith Jr." |
| Hyphenated names | Preserved as-is: "Obasanjo" |
| Names with prefixes | Standard splitting (no special handling needed for Nigerian names) |

### 3.3 Date Parsing

Normalizes multiple date formats to `YYYY-MM-DD`:
- `"01-October, 2013"` → `"2013-10-01"`
- `"2024-10-01"` → `"2024-10-01"`
- `"October 1, 2013"` → `"2013-10-01"`
- `datetime.datetime` objects from openpyxl → `"2013-10-01"`

---

## 4. Import Logic Design

### 4.1 Duplicate Resolution Strategy

When importing, each record is checked by the composite key `(last_name, first_name, department)`:

```
┌─────────────────────────────────────────────────────┐
│  Does record exist?  ─→  Yes  ─→  UPDATE existing   │
│      (by composite key)        (merge newer data)    │
│                              ─→  Add new phones     │
│                              ─→  Log as "updated"    │
│                                                    │
│                           No  ─→  INSERT new record │
│                                  Add phone numbers  │
│                                  Log as "added"      │
└─────────────────────────────────────────────────────┘
```

### 4.2 Format Auto-Detection

The `import_excel()` function scans the first 8 rows for identifying column names:
- Contains `"LAST NAME"` → NUC format
- Contains `"NAME"` + `"SEX"` → Newly Promoted format
- Neither → Error with clear message

### 4.3 Faculty Normalization

Discovered inconsistencies from data analysis:

| Raw (from Excel) | Normalized To |
|---|---|
| "Environmental Technoloty" | "Environmental Technology" |
| "College of Medical Science" | "College of Medical Sciences" |
| "Management Science" | "Management Sciences" |
| "Engineering and Engineering technology" | "Engineering and Engineering Technology" |

These mappings are stored in `app_settings` (key: `faculty_normalization`).

### 4.4 Phone Number Parsing

- Raw string from Excel split by `/, ; ` delimiters
- Minimum length: 7 characters (filters out garbage data)
- Each number stored as a separate row in `phone_numbers` table
- First phone marked as `is_primary=1`

---

## 5. Export Design

### 5.1 NUC Format Export

- **S/No. regenerated** on export (not stored in DB) — sequential row number
- **Default sort**: Faculty → Department → Last Name
- **Phone numbers**: Multiple phones joined with ` / ` delimiter
- **Retired professors**: Greyed out with strikethrough (or excluded by option)
- **ATBU branding**: Green header (#00843D), title row, footer attribution

### 5.2 Export Attribution

Footer: *"Generated by the ATBU Academic Planning Portal — Directorate of Academic Planning | Exported: YYYY-MM-DD HH:MM | Includes N professors"*

---

## 6. Import Results (Actual Run)

| File | Added | Updated | Skipped | Total |
|---|---|---|---|---|
| NUC Format | 171 | 1 | 0 | 172 |
| Newly Promoted | 54 | 0 | 1 | 54 |
| **Total** | **225** | **1** | **1** | **226 rows processed** |

### 6.1 Database State After Import

| Metric | Value |
|---|---|
| Total professors | 225 |
| Active professors | 225 |
| Professors with phone numbers | 187 (out of 225) |
| Total phone numbers stored | 190 |
| Distinct faculties | 12 |
| Import history entries | 2 |

### 6.2 Faculty Distribution

| Faculty | Count |
|---|---|
| Science | 46 |
| Agriculture and Agricultural Technology | 45 |
| Engineering and Engineering Technology | 32 |
| Technology Education | 27 |
| Environmental Technology | 25 |
| College of Medical Sciences | 19 |
| Management Sciences | 14 |
| Veterinary Medicine (FVM) | 9 |
| _Others_ | 8 |

---

## 7. Key Decisions Made

1. **SQLite over PostgreSQL/MySQL** — Data is 225 professors, fits in a portable file
2. **SQLAlchemy ORM** — Already in appdev-env, provides migration path, type safety
3. **Composite unique key** — Based on real data analysis, enables safe re-import
4. **Separate phone table** — Spec requirement for multiple phones, normalized design
5. **Faculty normalization map** — Discovered 5 naming inconsistencies in real data
6. **Flet native charts** (future) — No matplotlib needed, Flet has built-in BarChart/PieChart
7. **Password hashing with bcrypt** (future) — appdev-conda has bcrypt installed

---

## 8. Known Limitations (Phase 1)

| Limitation | Planned Fix |
|---|---|
| No password protection yet | Phase 2/3 |
| No Flet UI | Phase 2 |
| No charts/dashboard | Phase 2 |
| Phone normalization (080 vs +234) | Phase 2/3 improvement |
| No faculty inference for Newly Promoted imports | Future enhancement |
| No manual duplicate merging UI | Phase 2 |

---

## 9. Files Created

| File | Lines | Purpose |
|---|---|---|
| `database.py` | ~180 | SQLAlchemy models, DB init, session factory |
| `name_parser.py` | ~175 | Name splitting, date parsing, year extraction |
| `import_export.py` | ~385 | Import both formats, export NUC format, auto-detection |
| `run_import.py` | ~100 | Test script — imports both files + verification |
| `PHASE1_LOG.md` | ~200 | This documentation |

---

*End of Phase 1 Implementation Log*
