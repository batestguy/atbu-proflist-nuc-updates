# ATBU Academic Planning Portal

**ATBU Professors List & NUC Updates Manager**

A desktop application for managing professor records at Abubakar Tafawa Balewa University (ATBU), built for the Director of Academic Planning, **Prof. Abdulkadir Ahmed**.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-0.86.3-green)
![SQLite](https://img.shields.io/badge/SQLite-3-orange?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 📊 Dashboard
- Real-time statistics: Total professors, Active, Retired, Faculties, Departments
- Visual charts: Professors by Faculty (bar chart), Professors by Gender
- Quick overview of database health

### 👨‍🏫 Professor Management
- **223 professor records** (216 active, 7 retired)
- Searchable/filterable DataTable with 8 columns
- Color-coded status chips: All 🟢 | Active 🔵 | Retired 🔴 | Edit Mode 🟡
- Inline copy-to-clipboard for professor details
- Password-protected editing with confirmation dialogs

### 📥 Import/Export
- **NUC Format Export** — Generates Excel files in the format required by the National Universities Commission
- **Excel Import** — Auto-detects 3-section Excel format with professor data
- **Backup Database** — One-click SQLite backup to any location
- **Import History** — Tracks last 10 imports with stats

### 🔐 Security
- Password-protected editing (bcrypt hashed)
- Emergency password reset
- Role-based access control

### 🎨 ATBU Branding
- Custom sidebar with ATBU logo and colors
- Personalized for the Director of Academic Planning
- Version 1.1.0

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/batestguy/atbu-proflist-nuc-updates.git
cd atbu-proflist-nuc-updates

# Create virtual environment
python -m venv appdev-env
source appdev-env/bin/activate  # Linux/Mac
# or
appdev-env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
python main.py
```

### Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data assets;assets --add-data data;data --hidden-import bcrypt --hidden-import sqlalchemy --hidden-import openpyxl main.py
```

---

## 📁 Project Structure

```
atbu_professors_app/
├── main.py                    # App controller, sidebar, navigation
├── database.py                # SQLAlchemy models, init_db()
├── import_export.py           # Excel import/export logic
├── name_parser.py             # Name splitting, date normalization
├── ui_helpers.py              # UI utilities (snack bars, dialogs)
├── atbu_icons.py              # Material icon constants
├── screens/
│   ├── dashboard.py           # Stats cards + charts
│   ├── professors_list.py     # Searchable professor table
│   ├── add_professor.py       # Manual entry + Excel upload
│   ├── about.py               # Director's profile + ATBU info
│   ├── settings.py            # Password + DB management
│   └── import_export_screen.py # Import/Export UI
├── assets/
│   └── atbu_logo.png          # ATBU logo
└── data/
    └── professors.db          # SQLite database
```

---

## 📊 Database Schema

| Table | Description |
|-------|-------------|
| `professors` | 223 records with name, faculty, department, specialization, email |
| `phone_numbers` | One-to-many: multiple phones per professor |
| `app_settings` | Password hash, configuration |
| `import_history` | Last 10 import records |

---

## 🛠️ Tech Stack

- **Frontend:** [Flet](https://flet.dev) 0.86.3 (Flutter-based Python UI)
- **Database:** SQLite 3 + SQLAlchemy 2.0
- **Excel:** openpyxl for import/export
- **Auth:** bcrypt for password hashing
- **Packaging:** PyInstaller for .exe distribution

---

## 📋 NUC Format

The app generates Excel files in the **National Universities Commission (NUC)** format for professor list updates, including:
- Faculty name
- Department name
- Area of specialization
- Date of professorship
- Retirement/death/transfer status

---

## 👨‍💻 About

**Innovation by:** Prof. Abdulkadir Ahmed  
**Position:** Director of Academic Planning, ATBU  
**Purpose:** Streamline professor record management for NUC accreditation and internal planning

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **ATBU** — Abubakar Tafawa Balewa University
- **NUC** — National Universities Commission
- **Flet Team** — For the amazing Flutter-based Python UI framework
- **SQLAlchemy** — For the robust ORM
