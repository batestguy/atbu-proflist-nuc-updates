# ATBU Academic Planning Portal — Remaining Errors & Fixes Spec

**Date:** July 30, 2026  
**Status:** Pre-fix audit — all issues mapped, awaiting implementation  
**Flet Version:** 0.86.3 (verified)  
**Database:** 223 professors (216 active, 7 retired), 9 faculties, 75 depts, 182 phones

---

## Executive Summary

The app runs and all 6 screens load. The tkinter filedialog fix resolved the "Unknown control: FilePicker" error. However, **14 issues** remain across 3 priority tiers. This spec maps every issue with its exact location, root cause, and proposed fix.

---

## 🔴 CRITICAL (App-breaking or data-corrupting)

### C1. `session.query(Model).get(id)` Deprecated — Will Break in SQLAlchemy 2.0+

| Field | Detail |
|-------|--------|
| **Files** | `screens/professors_list.py` lines 357, 490 |
| **Root Cause** | `.get()` is a legacy Query method deprecated in SQLAlchemy 1.4+, removed in 2.0 |
| **Current Code** | `session.query(Professor).get(prof.id)` |
| **Error When** | SQLAlchemy upgrade to 2.0+ |
| **Fix** | Replace with `session.get(Professor, prof.id)` — works in both 1.4 and 2.0 |
| **Impact** | Edit professor and toggle retired will break on upgrade |

### C2. `datetime.utcnow` Deprecated — Warning on Python 3.12+

| Field | Detail |
|-------|--------|
| **Files** | `database.py` lines (model defaults), `screens/professors_list.py` line 417 |
| **Root Cause** | `datetime.utcnow()` is deprecated since Python 3.12, emits DeprecationWarning |
| **Current Code** | `default=datetime.utcnow` in Column defaults; `datetime.utcnow()` in `_save_edit` |
| **Fix** | Use `datetime.now(timezone.utc)` — add `from datetime import datetime, timezone` |
| **Impact** | Warnings flood logs; future Python versions may remove it |

### C3. `init_db()` Creates Duplicate Engine

| Field | Detail |
|-------|--------|
| **File** | `database.py` line 226 |
| **Root Cause** | Module has global `engine` at line 62, but `init_db()` creates a NEW engine at line 226 |
| **Current Code** | `engine = create_engine(f"sqlite:///{DB_PATH}", echo=echo)` inside `init_db()` |
| **Fix** | Remove the local `engine` variable in `init_db()`, use the module-level `engine` |
| **Impact** | Two engine pools compete for the same SQLite file; `get_session()` uses the module engine, `init_db()` uses a throwaway one |

---

## 🟡 HIGH PRIORITY (Visible bugs or UX failures)

### H1. Settings Screen Shows Hardcoded Database Path

| Field | Detail |
|-------|--------|
| **File** | `screens/settings.py` line 85 |
| **Root Cause** | Path is hardcoded as string literal |
| **Current Code** | `"D:\\Apps for ATBU\\atbu_professors_app\\data\\professors.db"` |
| **Fix** | Import `DB_PATH` from `database.py` and use it dynamically |
| **Impact** | Misleading if app is moved or run from .exe |

### H2. Faculty Field Not Editable in Edit Dialog

| Field | Detail |
|-------|--------|
| **File** | `screens/professors_list.py` `_edit_professor()` method |
| **Root Cause** | Edit dialog only exposes Dept, Spec, Email, Phone — not Faculty |
| **Fix** | Add `faculty_field = TextField(label="Faculty", value=p.faculty, width=400)` and save it in `_save_edit()` |
| **Impact** | Faculty name corrections require database manual edits |

### H3. Gender Chart Shows Misleading "80% Unknown"

| Field | Detail |
|-------|--------|
| **File** | `screens/dashboard.py` `_get_gender_data()` |
| **Root Cause** | Only 45/223 records have SEX data (only Newly Promoted format has SEX column) |
| **Fix** | Option A: Hide chart when <50% data exists. Option B: Show as "Data Incomplete: 45/223 records have gender data" |
| **Impact** | Confusing for Director; looks like a bug |

### H4. Import Does Not Process Retired Professors from NUC Format

| Field | Detail |
|-------|--------|
| **File** | `import_export.py` |
| **Root Cause** | The NUC Excel file has a "Retired" section with columns: Last Name, First Name, Other Names, Date, Status, Department. The 3-section parser detects it but may not properly create retired records |
| **Current State** | 7 retired professors were manually inserted via SQL, not imported |
| **Fix** | Ensure `import_nuc_format()` extracts retired section rows with `is_retired=1` and `retirement_status` set |
| **Impact** | Re-importing NUC file may overwrite the 7 manually-added retired professors |

### H5. No Confirmation Dialog Before Destructive Actions

| Field | Detail |
|-------|--------|
| **File** | `screens/settings.py` `_emergency_reset()` |
| **Root Cause** | Emergency password reset shows confirmation dialog, but `mark_retired` toggle in professors_list.py does NOT |
| **Fix** | Add confirmation before `_toggle_retired()` — "Mark [Name] as retired?" |
| **Impact** | Accidental clicks could toggle retirement status |

---

## 🟢 MEDIUM PRIORITY (Code quality, warnings, dead code)

### M1. Unused Imports in `add_professor.py`

| Field | Detail |
|-------|--------|
| **File** | `screens/add_professor.py` line 17 |
| **Root Cause** | `Tabs, Tab, RadioGroup, Radio` imported but never used |
| **Fix** | Remove unused imports to clean up the module |
| **Impact** | Minor: wasted memory, linter warnings |

### M2. DataTable Width May Still Clip Long Names

| Field | Detail |
|-------|--------|
| **File** | `screens/professors_list.py` line 275 |
| **Root Cause** | DataTable `width=1800` with 8 columns; some professor names + year exceed column width |
| **Fix** | Option A: Increase to `width=2200`. Option B: Make columns resizable. Option C: Truncate with tooltip showing full name |
| **Impact** | Some names still partially hidden |

### M3. `init_db()` Called on Every App Start

| Field | Detail |
|-------|--------|
| **File** | `database.py` `init_db()`, called from `main.py` `__init__` |
| **Root Cause** | `init_db()` runs `Base.metadata.create_all()` + inserts defaults every time |
| **Fix** | Add early return if tables already exist: `if engine.dialect.has_table(engine, 'professors'): return` |
| **Impact** | Minor performance overhead on startup |

### M4. Import Progress Not Shown During Long Operations

| Field | Detail |
|-------|--------|
| **Files** | `screens/import_export_screen.py`, `screens/add_professor.py` |
| **Root Cause** | Import shows "Importing..." snackbar but the operation blocks the UI thread |
| **Fix** | Add a ProgressBar or "Please wait..." overlay during import. Consider threading for large files |
| **Impact** | UI freezes during 200+ record imports |

### M5. No Error Handling for Missing ATBU Logo

| Field | Detail |
|-------|--------|
| **File** | `main.py` sidebar |
| **Root Cause** | If `assets/atbu_logo.png` is missing, falls back to emoji "🏛️" — but no warning shown |
| **Fix** | Log a warning when logo is missing; consider embedding a default |
| **Impact** | .exe distribution may miss the assets folder |

### M6. `Dropdown` Constructor Import May Need `dropdown` Namespace

| Field | Detail |
|-------|--------|
| **Files** | `screens/professors_list.py`, `screens/add_professor.py` |
| **Root Cause** | Both `DropdownOption` and `dropdown.Option` work in Flet 0.86.3 (verified), but mixing styles is inconsistent |
| **Fix** | Standardize on one approach: either `ft.DropdownOption` everywhere or `ft.dropdown.Option` everywhere |
| **Impact** | Code consistency |

---

## 🔵 LOW PRIORITY (Polish, enhancements)

### L1. Version and Date Hardcoded in About Page

| Field | Detail |
|-------|--------|
| **File** | `screens/about.py` lines ~230-234 |
| **Root Cause** | Version "1.0.0 (Desktop)" and "Last Updated: 2026-07-28" are string literals |
| **Fix** | Import version from a `__version__` variable or read from `app_settings` |

### L2. No Hover Effects on Interactive Elements

| Field | Detail |
|-------|--------|
| **Files** | All screen files |
| **Fix** | Add `animate_opacity=300`, `on_hover` handlers to buttons and cards |

### L3. No Data Backup/Restore Feature

| Field | Detail |
|-------|--------|
| **Files** | `screens/settings.py` |
| **Fix** | Add "Backup Database" button that copies `professors.db` to user-chosen location |

### L4. No Print Support for NUC Reports

| Field | Detail |
|-------|--------|
| **Files** | `screens/import_export_screen.py` |
| **Fix** | Add "Print Report" button that opens the exported Excel in default app |

### L5. Search Does Not Match Phone Numbers

| Field | Detail |
|-------|--------|
| **File** | `screens/professors_list.py` `_get_filtered()` |
| **Root Cause** | Search checks name, email, dept, spec, faculty — but NOT phone numbers |
| **Fix** | Add phone number to the search query check |

---

## Implementation Priority Order

| Phase | Issues | Est. Effort |
|-------|--------|-------------|
| **Phase A** (Critical) | C1, C2, C3 | 30 min |
| **Phase B** (High) | H1, H2, H3, H4, H5 | 1.5 hours |
| **Phase C** (Medium) | M1, M2, M3, M4, M5, M6 | 1 hour |
| **Phase D** (Low) | L1, L2, L3, L4, L5 | 2 hours |
| **Total** | 14 issues | ~5 hours |

---

## Files Requiring Changes

| File | Issues |
|------|--------|
| `database.py` | C2, C3, M3 |
| `screens/professors_list.py` | C1, C2, H2, H5, M2, M4, L5 |
| `screens/settings.py` | H1, L3 |
| `screens/dashboard.py` | H3 |
| `screens/add_professor.py` | M1, M6, M4 |
| `screens/about.py` | L1 |
| `screens/import_export_screen.py` | H4, M4, L4 |
| `import_export.py` | H4 |
| `main.py` | M5 |

---

## Flet 0.86.3 API Compatibility Matrix (Verified)

| API | Status | Notes |
|-----|--------|-------|
| `DropdownOption(text=, key=)` | ✅ | Use this or `dropdown.Option` |
| `Dropdown(on_select=)` | ✅ | **Do NOT use `on_change`** — it will crash |
| `Chip(on_click=)` | ✅ | Works correctly |
| `ResponsiveRow` | ✅ | Works with `col={}` dicts |
| `RadioGroup + Radio` | ✅ | Works but unused currently |
| `Colors.WHITE` etc. | ✅ | Uppercase enum is correct |
| `FontWeight.BOLD` | ✅ | Uppercase enum is correct |
| `Alignment.CENTER` | ✅ | Uppercase enum is correct |
| `BoxFit.CONTAIN` | ✅ | Uppercase enum is correct |
| `FilePicker` | ❌ | **Broken** — use tkinter.filedialog |
| `NavigationRail(extended=True)` | ❌ | **Clips items** — use custom nav |
| `page.show_snack_bar()` | ❌ | Does not exist — use overlay SnackBar |
| `page.dialog` | ❌ | Does not exist — use `page.show_dialog()` |

---

*Generated by audit of all 11 Python source files + Flet 0.86.3 runtime verification.*
