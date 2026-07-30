# ATBU Academic Planning Portal — Project Architecture

> **Project:** Desktop application for managing ATBU professors database
> **Location:** `D:\Apps for ATBU\atbu_professors_app\`
> **Tech Stack:** Python 3.x + Flet 0.86.3 + SQLAlchemy + SQLite
> **Status:** ✅ Phase 1 (Foundation) + Phase 2 (UI) + Phase 3 (Launch) Complete

---

## 1. Project Structure

```
atbu_professors_app/
│
├── main.py                    # Entry point — Flet app scaffold, sidebar, nav, password system
├── database.py                # SQLAlchemy models + DB initialization
├── name_parser.py             # Full name splitting + date normalization utilities
├── import_export.py           # Excel import (NUC + Newly Promoted) + NUC format export
├── run_import.py              # One-time import script for loading Excel data
│
├── screens/
│   ├── dashboard.py           # Stats cards + Container-based bar/pie charts
│   ├── professors_list.py     # Searchable DataTable with copy, edit, filters
│   ├── add_professor.py       # Manual entry form + Excel upload
│   ├── about.py               # Director profile + ATBU branding
│   ├── settings.py            # Password change + database info + export
│   └── import_export_screen.py # Import/export with file pickers + history
│
├── assets/
│   └── atbu_logo.png          # Official ATBU logo (279KB)
│
├── data/
│   └── professors.db          # SQLite database (auto-created on first run)
│
├── launch_app.bat             # Windows double-click launcher
│
├── PHASE1_LOG.md              # Foundation layer documentation
├── PHASE2_LOG.md              # Desktop UI documentation
├── PROJECT_ARCHITECTURE.md    # This file
│
└── knowledge.md               # Short project reference
```

---

## 2. Database Schema (SQLite via SQLAlchemy)

### Table: `professors`
| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-increment ID |
| `last_name` | String(100) | Surname |
| `first_name` | String(100) | First name |
| `other_names` | String(200) | Middle/other names (nullable) |
| `date_of_professorship` | String(20) | Normalized YYYY-MM-DD date |
| `added_year` | Integer | Extracted year for grouping |
| `faculty` | String(200) | Faculty name |
| `department` | String(200) | Department name |
| `area_of_specialization` | String(300) | Specialization area |
| `sex` | String(10) | M/F (nullable) |
| `email` | String(200) | Email (nullable) |
| `is_retired` | Integer | 0=Active, 1=Retired |
| **UNIQUE** | `(last_name, first_name, department)` | Composite unique key for duplicate handling |
| **INDEX** | `faculty` | For fast faculty filtering |
| **INDEX** | `department` | For fast dept filtering |
| **INDEX** | `area_of_specialization` | For fast spec filtering |
| **INDEX** | `last_name` | For search |
| **INDEX** | `added_year` | For year grouping |

### Table: `phone_numbers`
| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-increment ID |
| `professor_id` | Integer FK → professors.id | Parent professor |
| `phone` | String(50) | Phone number |
| `is_primary` | Integer | 1=Primary, 0=Secondary |

### Table: `app_settings`
| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-increment ID |
| `key` | String(100) UNIQUE | Setting key |
| `value` | Text | Setting value |

**Default entries:**
- `password_hash` — bcrypt hashed admin password
- `faculty_normalization` — JSON mapping for faculty name inconsistencies

### Table: `import_history`
| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-increment ID |
| `filename` | String(500) | Imported file name |
| `source_format` | String(50) | "nuc_format" or "newly_promoted" |
| `records_added` | Integer | New records |
| `records_updated` | Integer | Updated duplicates |
| `records_skipped` | Integer | Skipped entries |
| `imported_at` | DateTime | Timestamp |

---

## 3. Application Flow

### 3.1 Startup Sequence
1. `main.py` runs → `ft.app(target=main)` starts Flet GUI
2. `AcademicPlanningApp.__init__()` called with the Page object
3. `init_db()` creates all tables + indexes (if not exists)
4. `_check_password_setup()` queries `app_settings` for password_hash
5. `_build_ui()` creates sidebar, content area, password dialogs
6. If no password set → first-time setup dialog appears
7. Dashboard (index 0) loads as default screen

### 3.2 Navigation
- **Left sidebar** with 6 NavigationRail items:
  1. Dashboard (index 0)
  2. All Professors (index 1)
  3. Add Professor (index 2)
  4. Import / Export (index 3)
  5. About (index 4)
  6. Settings (index 5)
- Clicking a nav item → `_on_nav_change` → `_rebuild_sidebar()` → `_load_screen(index)`
- Each screen is a class with `__call__` method returning a Flet Control

### 3.3 Password System
- **First launch:** `_setup_dialog` prompts to create admin password (min 6 chars)
- **Lock state:** `is_unlocked` boolean flag on the app controller
- **Toggle:** Click lock icon in sidebar → prompt for password → verify via bcrypt
- **Auto-reflect:** Sidebar footer shows "Editing: On" (green) / "Editing: Off" (grey)
- **Password change:** Settings screen with current + new password verification
- **Emergency reset:** Settings → clears password_hash from DB → restart to set new

---

## 4. Screen-by-Screen Details

### 4.1 Dashboard (`screens/dashboard.py`)
**Purpose:** High-level overview with statistics and visualizations

**Components:**
- **Stats Cards (6):** Total, Active, Retired, Faculties, Departments, Phone Numbers
- **Bar Charts (4):** Faculty distribution, Top 10 Departments, Year of Appointment, Top 8 Specializations
- **Pie Chart Alternatives (2):** Gender distribution, Active vs Retired

**Chart Implementation (critical!):**
> Flet 0.86.3 does NOT include BarChart, PieChart, or any chart widgets.
> All visualizations use Container-based custom rendering:
> - **Bar charts:** Colored Containers with proportional heights + spacer divs for baseline alignment
> - **Pie charts:** Horizontal stacked bar segments + color legend with percentages

### 4.2 Professors List (`screens/professors_list.py`)
**Purpose:** Search, filter, view, copy, and edit professor records

**Features:**
- Search bar (name, email, specialization, faculty)
- Faculty dropdown filter
- Department dropdown filter
- Status chips: All / Active / Retired
- Copy details to clipboard (pyperclip with fallback dialog)
- Edit dialog (password-protected):
  - View/edit department, specialization, email
  - Mark as Retired toggle
- **Approach:** Loads all professors into `_professors_cache` on init, filters in-memory on search/filter changes

### 4.3 Add Professor (`screens/add_professor.py`)
**Purpose:** Manual entry form + Excel file upload

**Features:**
- **Lock screen:** Shows unlock prompt if not unlocked
- **Manual form:** Name (3 fields), Date, Sex dropdown, Faculty dropdown, Department dropdown, Specialization, Email, Phone
- **Excel upload:** File picker for .xlsx files → auto-detect format → import
- **Validation:** Checks required fields before submission
- **Duplicate handling:** Uses same `import_excel()` function — updates if exists

### 4.4 Import / Export (`screens/import_export_screen.py`)
**Purpose:** Bulk data operations

**Features:**
- **Import:** Select .xlsx → auto-detect NUC vs Newly Promoted format → import with progress snackbar
- **Export to default** location
- **Export to custom** location with save file picker
- **Import history** (last 10 imports)
- All operations disabled when locked

### 4.5 About (`screens/about.py`)
**Purpose:** Director profile, ATBU branding, and app info

**Sections:**
1. **Director Profile Card:** Abdulkadir Ahmed, Director of Academic Planning (green circle with "AA" initials)
2. **ATBU Branding Card:** University name, motto ("Doctrina Mater Artium"), translation
3. **App Info Card:** Version, Technology, DB count, Last Updated, Developer

### 4.6 Settings (`screens/settings.py`)
**Purpose:** Configuration and maintenance

**Features:**
- **Password change:** Current → New → Confirm (with bcrypt verification)
- **Database info:** Location, total professors, faculties count
- **Export NUC format** button
- **Emergency password reset** (clears hash, requires app restart)

---

## 5. Data Import/Export Pipeline

### 5.1 Import (`import_export.py`)

**Auto-Detection Logic:**
1. Open .xlsx file
2. Scan header row for identifying columns
3. If "LAST NAME" found → NUC format
4. If "NAME" + "SEX" found → Newly Promoted format
5. Parse rows based on detected format

**Duplicate Resolution:**
- Composite unique key: `(last_name, first_name, department)`
- If match found → UPDATE existing record
- If no match → INSERT new record
- Phone numbers are split by `/` delimiter and stored in separate `phone_numbers` table

**Faculty Normalization:**
- Maps inconsistent faculty names to canonical versions
- E.g., "College of Medical Science" → "College of Medical Sciences"

### 5.2 Export (`import_export.py`)

**NUC Format Export:**
- Creates Excel with ATBU header branding
- Columns: SN, NAMES, RANK, SEX, BIRTH, QUAL, SPECIALIZATION, DEPARTMENT, FACULTY, PHONE, EMAIL, D.O.L.P, etc.
- Includes Directorate of Academic Planning attribution

---

## 6. Name Parser (`name_parser.py`)

**Functions:**

| Function | Purpose |
|---|---|
| `split_full_name(full_name)` | Splits "First Last" → `(last_name, first_name, other_names)` |
| `parse_nuc_date(date_str)` | Normalizes multiple date formats → "YYYY-MM-DD" |
| `get_year_from_date(date_str)` | Extracts year from date string |

**Supported Date Formats:**
- `YYYY-MM-DD` (already normalized)
- `DD-Month-YYYY` (e.g., "1-October-2013")
- `DD/MM/YYYY` (e.g., "01/10/2013")
- `Month DD, YYYY` (e.g., "October 1, 2013")
- `DD Month YYYY` (e.g., "1 October 2013")

---

## 7. Key Design Decisions

### 7.1 Why Container-based charts instead of matplotlib/plotly?
- Flet 0.86.3 has NO built-in chart widgets
- matplotlib took too long to install and adds dependency weight
- Container-based approach: zero dependencies, guaranteed to work, syncs with Flet layout

### 7.2 Why composite unique key on (last_name, first_name, department)?
- Some professors share same name but different departments
- Some professors appear in both NUC and Newly Promoted files
- The combination of name + department uniquely identifies a professor

### 7.3 Why separate phone_numbers table?
- Some professors have multiple phone numbers (delimited by `/`)
- Normalized design allows querying/filtering by phone
- Avoids string parsing for phone-related operations

### 7.4 Why full sidebar rebuild on navigation?
- Flet NavigationRail does not support dynamic `trailing` reassignment in 0.86.3
- Full rebuild ensures lock button state and nav highlighting are always in sync
- Trade-off: slightly more expensive on each nav click (negligible for desktop app)

---

## 8. Environment

| Component | Path |
|---|---|
| **Python env** | `D:\appdev-env\Scripts\python.exe` |
| **Project root** | `D:\Apps for ATBU\atbu_professors_app\` |
| **Database** | `D:\Apps for ATBU\atbu_professors_app\data\professors.db` |
| **ATBU logo** | `D:\Apps for ATBU\atbu_professors_app\assets\atbu_logo.png` |

### Installed Packages
- `flet` 0.86.3 (GUI framework)
- `sqlalchemy` (ORM)
- `openpyxl` (Excel handling)
- `bcrypt` (password hashing)
- `pyperclip` (clipboard, optional with fallback)

---

## 9. Known Limitations & Future Work

| Limitation | Priority | Suggested Fix |
|---|---|---|
| No auto-lock timer (15 min inactivity) | Medium | Add inactivity timer in main.py |
| Bar chart labels may wrap inconsistently | Low | Use fixed-width containers for all labels |
| Edit dialog is simplified (not full form) | Medium | Create full ProfessorDetailScreen |
| No data backup/restore | Low | Add backup button in settings |
| No multi-user support | Low | Add user accounts table |
| No web version | High | Would need separate web app (Django/Flask) |
| `pyperclip` not installed by default | Low | Add to requirements.txt |
