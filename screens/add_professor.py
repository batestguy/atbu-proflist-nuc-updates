"""
screens/add_professor.py — Manual entry form + Excel upload for adding professors
ATBU Academic Planning Portal
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from flet import (
    Container, Column, Row, Text, Card, TextField, Dropdown,
    DropdownOption, FilledButton, OutlinedButton,
    Icon, Padding, Margin, Colors,
    MainAxisAlignment, CrossAxisAlignment, FontWeight,
    ScrollMode, ResponsiveRow, Alignment
)
import atbu_icons as icons
from database import get_session, Professor, PhoneNumber, AppSetting
from import_export import import_excel, import_nuc_format, import_newly_promoted
from ui_helpers import show_snack, pick_file

ATBU_GREEN = "#00843D"
ATBU_GOLD = "#F5A623"
ATBU_DARK = "#1A1A2E"
ATBU_BG = "#F5F7FA"
ATBU_MUTED = "#6B7280"


class AddProfessorScreen:
    """Screen for adding professors via form or Excel upload."""

    def __init__(self, app):
        self.app = app
        self.page = app.page
        self._faculties = []
        self._departments = []
        self._load_options()
        
        # Form fields
        self.last_name = TextField(label="Last Name *", width=300)
        self.first_name = TextField(label="First Name *", width=300)
        self.other_names = TextField(label="Other Names", width=300)
        self.date_picker = TextField(label="Date of Professorship *", 
                                     hint_text="YYYY-MM-DD or DD-Month-YYYY", width=300)
        self.faculty_dropdown = Dropdown(label="Faculty *", width=300,
                                         options=[DropdownOption(f, f) for f in self._faculties])
        self.dept_dropdown = Dropdown(label="Department *", width=300,
                                      options=[DropdownOption(d, d) for d in self._departments])
        self.spec_field = TextField(label="Area of Specialization *", width=300)
        self.email_field = TextField(label="Email", width=300)
        self.phone_field = TextField(label="Phone Number", hint_text="One or more, use / to separate", width=300)
        self.sex_dropdown = Dropdown(label="Sex", width=150,
                                     options=[DropdownOption("M", "Male"), DropdownOption("F", "Female")])
        
    def _load_options(self):
        session = get_session()
        faculties = session.query(Professor.faculty).distinct().all()
        self._faculties = sorted(set(f[0] for f in faculties if f[0]))
        depts = session.query(Professor.department).distinct().all()
        self._departments = sorted(set(d[0] for d in depts if d[0]))
        session.close()
    
    def __call__(self):
        return self._build()
    
    def _build(self):
        """Build the add professor screen."""
        
        # Check if unlocked
        if not self.app.is_unlocked:
            return Container(
                content=Column([
                    Icon(icons.LOCK_OUTLINE, size=64, color=ATBU_MUTED),
                    Text("🔒 Editing is locked", size=20, weight=FontWeight.BOLD, 
                         color=ATBU_DARK),
                    Text("Click the lock icon in the sidebar to unlock editing.", 
                         size=14, color=ATBU_MUTED),
                    FilledButton("🔓 Unlock Now", 
                                 on_click=lambda _: self.app._show_password_dialog(),
                                 bgcolor=ATBU_GREEN, color=Colors.WHITE),
                ], horizontal_alignment=CrossAxisAlignment.CENTER),
                padding=Padding.all(100),
                alignment=Alignment.CENTER,
            )
        
        # Form section
        form_section = Card(
            content=Container(
                content=Column([
                    Text("👤 Add New Professor", size=18, weight=FontWeight.BOLD, 
                         color=ATBU_DARK),
                    Text("Fill in the details below. Fields marked with * are required.", 
                         size=12, color=ATBU_MUTED),
                    Container(height=12),
                    # Name row
                    ResponsiveRow([
                        Container(content=self.last_name, col={"sm": 12, "md": 4}),
                        Container(content=self.first_name, col={"sm": 12, "md": 4}),
                        Container(content=self.other_names, col={"sm": 12, "md": 4}),
                    ]),
                    # Date + Sex row
                    ResponsiveRow([
                        Container(content=self.date_picker, col={"sm": 12, "md": 4}),
                        Container(content=self.sex_dropdown, col={"sm": 12, "md": 3}),
                    ]),
                    # Faculty + Dept row
                    ResponsiveRow([
                        Container(content=self.faculty_dropdown, col={"sm": 12, "md": 6}),
                        Container(content=self.dept_dropdown, col={"sm": 12, "md": 6}),
                    ]),
                    # Specialization
                    ResponsiveRow([
                        Container(content=self.spec_field, col={"sm": 12, "md": 12}),
                    ]),
                    # Contact row
                    ResponsiveRow([
                        Container(content=self.email_field, col={"sm": 12, "md": 6}),
                        Container(content=self.phone_field, col={"sm": 12, "md": 6}),
                    ]),
                    Container(height=12),
                    # Submit button
                    FilledButton(
                        "💾 Save Professor",
                        on_click=self._save_professor,
                        bgcolor=ATBU_GREEN, color=Colors.WHITE,
                        width=200, height=44,
                    ),
                ]),
                padding=Padding.all(24),
            ),
            elevation=2,
        )
        
        # Excel upload section
        upload_section = Card(
            content=Container(
                content=Column([
                    Text("📂 Import from Excel", size=18, weight=FontWeight.BOLD, 
                         color=ATBU_DARK),
                    Text("Upload a properly formatted NUC format or Newly Promoted format (.xlsx) file.", 
                         size=12, color=ATBU_MUTED),
                    Container(height=12),
                    FilledButton(
                        "📤 Upload Excel File",
                        icon=icons.UPLOAD_FILE,
                        on_click=self._pick_excel_file,
                        bgcolor=Colors.BLUE_700, color=Colors.WHITE,
                        width=250,
                    ),
                    Container(
                        content=Text("Supports: NUC format (Last Name, First Name...) and "
                                    "Newly Promoted format (NAME, SEX, D.O.L.P...)",
                                    size=11, color=ATBU_MUTED),
                        padding=Padding.only(top=8),
                    ),
                ]),
                padding=Padding.all(24),
            ),
            elevation=2,
        )
        

        
        return Container(
            content=Column([
                Text("➕ Add Professor", size=28, weight=FontWeight.BOLD, 
                     color=ATBU_DARK),
                Text("Add new professors manually or import from Excel.", 
                     size=14, color=ATBU_MUTED),
                Container(height=16),
                form_section,
                Container(height=16),
                upload_section,

            ], scroll=ScrollMode.AUTO),
        )
    
    def _save_professor(self, e):
        """Save a new professor from the form."""
        # Validate required fields
        errors = []
        if not self.last_name.value: errors.append("Last Name")
        if not self.first_name.value: errors.append("First Name")
        if not self.date_picker.value: errors.append("Date of Professorship")
        if not self.faculty_dropdown.value: errors.append("Faculty")
        if not self.dept_dropdown.value: errors.append("Department")
        if not self.spec_field.value: errors.append("Area of Specialization")
        
        if errors:
            show_snack(self.page, f"❌ Required fields missing: {', '.join(errors)}", bgcolor=Colors.RED_400)
            return
        
        from name_parser import parse_nuc_date
        
        session = get_session()
        try:
            date_normalized = parse_nuc_date(self.date_picker.value)
            from import_export import parse_phones
            phones = parse_phones(self.phone_field.value)
            
            prof = Professor(
                last_name=self.last_name.value.strip(),
                first_name=self.first_name.value.strip(),
                other_names=self.other_names.value.strip() or None,
                date_of_professorship=date_normalized,
                faculty=self.faculty_dropdown.value,
                department=self.dept_dropdown.value,
                area_of_specialization=self.spec_field.value.strip(),
                email=self.email_field.value.strip() or None,
                sex=self.sex_dropdown.value or None,
            )
            session.add(prof)
            session.flush()
            
            for i, phone in enumerate(phones):
                session.add(PhoneNumber(
                    professor_id=prof.id, phone=phone,
                    is_primary=1 if i == 0 else 0
                ))
            
            session.commit()
            show_snack(self.page, f"✅ {prof.last_name}, {prof.first_name} added successfully!",
                       bgcolor=ATBU_GREEN, duration=3000)
            self._clear_form()
            
        except Exception as ex:
            session.rollback()
            show_snack(self.page, f"❌ Error: {str(ex)}", bgcolor=Colors.RED_400)
        finally:
            session.close()
    
    def _clear_form(self):
        """Clear all form fields after successful save."""
        for field in [self.last_name, self.first_name, self.other_names,
                      self.date_picker, self.spec_field, self.email_field,
                      self.phone_field]:
            field.value = ""
        self.faculty_dropdown.value = None
        self.dept_dropdown.value = None
        self.sex_dropdown.value = None
        self.page.update()
    
    def _pick_excel_file(self, e=None):
        """Open file picker for Excel upload using tkinter filedialog."""
        filepath = pick_file(title="Select NUC or Newly Promoted Excel file")
        if not filepath:
            return
        
        show_snack(self.page, f"📄 Importing: {os.path.basename(filepath)}...", duration=1000)
        self.page.update()
        
        try:
            import_result = import_excel(filepath)
            show_snack(self.page, f"✅ Import complete: {import_result['added']} added, "
                       f"{import_result['updated']} updated, {import_result['skipped']} skipped",
                       bgcolor=ATBU_GREEN, duration=4000)
        except Exception as ex:
            show_snack(self.page, f"❌ Import failed: {str(ex)}", bgcolor=Colors.RED_400, duration=5000)
        self.page.update()
