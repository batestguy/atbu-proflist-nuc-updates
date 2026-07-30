"""
screens/professors_list.py — Searchable/filterable professors table with edit + copy
ATBU Academic Planning Portal
"""

import os
import sys
from datetime import datetime, timezone

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from flet import (
    Container, Column, Row, Text, Card, DataTable, DataColumn, 
    DataRow, DataCell, TextField, Dropdown, DropdownOption,
    IconButton, Chip, Icon,
    Padding, Margin, Colors,
    MainAxisAlignment, CrossAxisAlignment, FontWeight,
    ScrollMode, ResponsiveRow, Alignment, Border, BorderSide,
    AlertDialog, FilledButton, OutlinedButton
)
import atbu_icons as icons
from database import get_session, Professor, PhoneNumber
from ui_helpers import show_dialog, close_dialog, show_snack

ATBU_GREEN = "#00843D"
ATBU_GOLD = "#F5A623"
ATBU_DARK = "#1A1A2E"
ATBU_BG = "#F5F7FA"
ATBU_MUTED = "#6B7280"


class ProfessorsListScreen:
    """Searchable, filterable table of all professors with copy and edit."""

    def __init__(self, app):
        self.app = app
        self.page = app.page
        self.search_query = ""
        self.filter_faculty = ""
        self.filter_dept = ""
        self.filter_retired = "active"  # "all", "active", "retired"
        self._professors_cache = []
        self._faculties = []
        self._departments = []
        self._load_data()
        
    def _load_data(self):
        """Load all professors and filter options."""
        session = get_session()
        try:
            self._professors_cache = session.query(Professor).order_by(
                Professor.faculty, Professor.department, Professor.last_name
            ).all()
            
            faculties = session.query(Professor.faculty).distinct().order_by(
                Professor.faculty).all()
            self._faculties = sorted(set(f[0] for f in faculties if f[0]))
            
            depts = session.query(Professor.department).distinct().order_by(
                Professor.department).all()
            self._departments = sorted(set(d[0] for d in depts if d[0]))
        finally:
            session.close()
    
    def __call__(self):
        return self._build()
    
    def _build(self):
        """Build the professors list screen."""
        
        # Search bar
        search_field = TextField(
            hint_text="🔍 Search by name, email, specialization...",
            on_change=self._on_search,
            prefix_icon=icons.SEARCH,
            border_radius=12,
            width=500,
            height=42,
            text_size=14,
        )
        
        # Filter dropdowns
        faculty_options = [DropdownOption("", "All Faculties")] + [
            DropdownOption(f, f[:35]) for f in self._faculties
        ]
        dept_options = [DropdownOption("", "All Departments")] + [
            DropdownOption(d, d[:35]) for d in self._departments
        ]
        
        faculty_filter = Dropdown(
            options=faculty_options,
            value=self.filter_faculty,
            on_select=self._on_faculty_filter,
            width=250,
            height=42,
            text_size=13,
        )
        dept_filter = Dropdown(
            options=dept_options,
            value=self.filter_dept,
            on_select=self._on_dept_filter,
            width=250,
            height=42,
            text_size=13,
        )
        
        # Status filter chips (rebuilt on each _refresh for correct colors)
        self._status_row_container = Container(content=self._build_status_row())
        
        # Results count
        filtered = self._get_filtered()
        self._result_count_ref = Text(
            f"Showing {len(filtered)} professors", 
            size=13, color=ATBU_MUTED
        )
        result_count = self._result_count_ref
        
        # Data table
        self._table_container = Container(content=self._build_table(filtered), expand=True)
        table_container = self._table_container
        
        # Header
        header = Container(
            content=Column([
                Text("📋 All Professors", size=28, weight=FontWeight.BOLD, 
                     color=ATBU_DARK),
                Text("Search, filter, and manage professor records", 
                     size=14, color=ATBU_MUTED),
            ]),
            margin=Margin.only(bottom=12),
        )
        
        # Filter bar
        filter_bar = Container(
            content=Column([
                Row([
                    search_field,
                    faculty_filter,
                    dept_filter,
                ], spacing=12, wrap=True),
                self._status_row_container,
            ]),
            margin=Margin.only(bottom=8),
        )
        
        return Container(
            content=Column([
                header,
                filter_bar,
                result_count,
                Container(height=8),
                table_container,
            ], scroll=ScrollMode.AUTO),
        )
    
    def _build_status_row(self):
        """Build the status filter chip row with correct colors.
        Chips are rebuilt on each refresh because Flet 0.86.3 Chip
        doesn't support dynamic bgcolor/color updates."""
        chip_all = Chip(
            label=Text("All", size=12, weight=FontWeight.BOLD),
            on_click=lambda _: self._set_status_filter("all"),
            bgcolor=ATBU_GREEN if self.filter_retired == "all" else Colors.GREY_400,
            color=Colors.WHITE,
        )
        chip_active = Chip(
            label=Text("Active", size=12, weight=FontWeight.BOLD),
            on_click=lambda _: self._set_status_filter("active"),
            bgcolor="#2196F3" if self.filter_retired == "active" else Colors.GREY_400,
            color=Colors.WHITE,
        )
        chip_retired = Chip(
            label=Text("Retired", size=12, weight=FontWeight.BOLD),
            on_click=lambda _: self._set_status_filter("retired"),
            bgcolor="#F44336" if self.filter_retired == "retired" else Colors.GREY_400,
            color=Colors.WHITE,
        )
        chip_edit = Chip(
            label=Text("Edit Mode 🔓" if self.app.is_unlocked else "Locked 🔒", 
                          size=12, weight=FontWeight.BOLD),
            bgcolor=ATBU_GOLD if self.app.is_unlocked else Colors.GREY_400,
            color=Colors.WHITE,
        )
        return Row([chip_all, chip_active, chip_retired, chip_edit], spacing=8)
    
    def _get_filtered(self):
        """Get filtered professors based on search and filters."""
        results = []
        for p in self._professors_cache:
            # Status filter
            if self.filter_retired == "active" and p.is_retired:
                continue
            if self.filter_retired == "retired" and not p.is_retired:
                continue
            
            # Faculty filter
            if self.filter_faculty and p.faculty != self.filter_faculty:
                continue
            
            # Department filter
            if self.filter_dept and p.department != self.filter_dept:
                continue
            
            # Search filter
            if self.search_query:
                q = self.search_query.lower()
                if not any([
                    q in p.last_name.lower(),
                    q in p.first_name.lower(),
                    q in (p.other_names or "").lower(),
                    q in p.department.lower(),
                    q in p.area_of_specialization.lower(),
                    q in (p.email or "").lower(),
                    q in p.faculty.lower(),
                    any(q in pn.phone.lower() for pn in p.phone_numbers),
                ]):
                    continue
            
            results.append(p)
        
        return results
    
    def _build_table(self, professors):
        """Build the data table from filtered professors."""
        
        columns = [
            DataColumn(Text("S/No", size=12, weight=FontWeight.BOLD), numeric=True),
            DataColumn(Text("Full Name", size=12, weight=FontWeight.BOLD)),
            DataColumn(Text("Faculty", size=12, weight=FontWeight.BOLD)),
            DataColumn(Text("Department", size=12, weight=FontWeight.BOLD)),
            DataColumn(Text("Specialization", size=12, weight=FontWeight.BOLD)),
            DataColumn(Text("Phone", size=12, weight=FontWeight.BOLD)),
            DataColumn(Text("Email", size=12, weight=FontWeight.BOLD)),
            DataColumn(Text("Actions", size=12, weight=FontWeight.BOLD)),
        ]
        
        rows = []
        for i, p in enumerate(professors, 1):
            phones = " / ".join(pn.phone for pn in p.phone_numbers)
            
            # Name with retired badge if applicable
            name_text = f"{p.last_name}, {p.first_name}"
            if p.other_names:
                name_text += f" {p.other_names}"
            
            # Build name text with year
            full_name = name_text
            if p.date_of_professorship:
                full_name += f" ({p.date_of_professorship[:4]})"
            retired_tag = " 🔴" if p.is_retired else ""
            
            rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(str(i), size=11, color=ATBU_MUTED)),
                        DataCell(Text(full_name + retired_tag, size=12, weight=FontWeight.BOLD)),
                        DataCell(Text(p.faculty[:25], size=11)),
                        DataCell(Text(p.department, size=11)),
                        DataCell(Text(p.area_of_specialization[:30], size=11)),
                        DataCell(Text(phones[:25], size=11)),
                        DataCell(Text((p.email or "")[:25], size=11)),
                        DataCell(
                            IconButton(
                                icon=icons.CONTENT_COPY,
                                icon_size=16,
                                icon_color=ATBU_MUTED,
                                tooltip="Copy details",
                                on_click=lambda _, prof=p: self._copy_details(prof),
                            )
                        ),
                    ],
                )
            )
        
        if not rows:
            return Container(
                content=Column([
                    Icon(icons.SEARCH_OFF, size=64, color=Colors.GREY_400),
                    Text("No professors match your filters", 
                         size=16, color=ATBU_MUTED),
                ], horizontal_alignment=CrossAxisAlignment.CENTER),
                padding=Padding.all(80),
            )
        
        return Column([
            DataTable(
                columns=columns,
                rows=rows,
                border=Border.all(width=0.5, color=Colors.GREY_300),
                border_radius=8,
                heading_row_color=ATBU_GREEN,
                heading_row_height=40,
                data_row_min_height=48,
                data_row_max_height=60,
                column_spacing=16,
                horizontal_margin=12,
                width=2000,
            ),
        ], scroll=ScrollMode.AUTO)
    
    def _on_search(self, e):
        """Handle search input change."""
        self.search_query = e.control.value
        self._refresh()
    
    def _on_faculty_filter(self, e):
        """Handle faculty filter change."""
        self.filter_faculty = e.control.value
        self._refresh()
    
    def _on_dept_filter(self, e):
        """Handle department filter change."""
        self.filter_dept = e.control.value
        self._refresh()
    
    def _set_status_filter(self, status):
        """Set the retired/active filter."""
        self.filter_retired = status
        self._refresh()
    
    def _refresh(self):
        """Update the content area in-place without recreating the screen.
        This preserves search_query and filter state across refreshes."""
        self._load_data()
        filtered = self._get_filtered()
        result_count = self._result_count_ref
        table = self._build_table(filtered)
        # Update the result count text
        result_count.value = f"Showing {len(filtered)} professors"
        # Replace the table container content
        self._table_container.content = table
        # Rebuild filter chips with correct colors (Flet Chip doesn't support dynamic updates)
        self._status_row_container.content = self._build_status_row()
        self.page.update()
    
    def _copy_details(self, prof):
        """Copy professor details to clipboard."""
        session = get_session()
        try:
            p = session.get(Professor, prof.id)
            phones = " / ".join(pn.phone for pn in p.phone_numbers) if p else ""
            
            details = (
                f"Name: {p.last_name}, {p.first_name} {p.other_names or ''}\n"
                f"Faculty: {p.faculty}\n"
                f"Department: {p.department}\n"
                f"Specialization: {p.area_of_specialization}\n"
                f"Date of Professorship: {p.date_of_professorship}\n"
                f"Email: {p.email or 'N/A'}\n"
                f"Phone: {phones or 'N/A'}\n"
                f"Status: {'Retired' if p.is_retired else 'Active'}"
            )
        finally:
            session.close()
        
        if HAS_PYPERCLIP:
            try:
                pyperclip.copy(details)
                show_snack(self.page, "✅ Details copied to clipboard", duration=1500, bgcolor=ATBU_GREEN)
            except Exception:
                self._show_copy_dialog(details)
        else:
            self._show_copy_dialog(details)
    
    def _show_copy_dialog(self, details):
        """Show copy dialog as fallback."""
        dlg = AlertDialog(
            title=Text("Professor Details"),
            content=Text(details, size=12, selectable=True),
            actions=[OutlinedButton("Close", on_click=lambda e: close_dialog(self.page))],
        )
        show_dialog(self.page, dlg)
    
    def _edit_professor(self, prof):
        """Open edit dialog for a professor (password required)."""
        if not self.app.is_unlocked:
            self.app._show_password_dialog()
            return
        
        session = get_session()
        try:
            p = session.get(Professor, prof.id)
            if not p:
                show_snack(self.page, "❌ Professor not found", bgcolor=Colors.RED_400)
                return
            
            # Store field references for save
            self._edit_fields = {}
            
            name_field = TextField(label="Full Name", 
                                  value=f"{p.last_name}, {p.first_name} {p.other_names or ''}",
                                  read_only=True, width=400)
            faculty_field = TextField(label="Faculty", value=p.faculty or "", width=400)
            dept_field = TextField(label="Department", value=p.department or "", width=400)
            spec_field = TextField(label="Specialization", value=p.area_of_specialization or "", width=400)
            email_field = TextField(label="Email", value=p.email or "", width=400)
            phone_field = TextField(label="Phone(s)", 
                                   value=" / ".join(pn.phone for pn in p.phone_numbers),
                                   width=400,
                                   hint_text="Separate multiple with /")
            
            self._edit_fields = {
                "faculty": faculty_field,
                "dept": dept_field,
                "spec": spec_field,
                "email": email_field,
                "phone": phone_field,
            }
            
            dlg = AlertDialog(
                title=Text(f"✏️ Edit: {p.last_name}, {p.first_name}"),
                content=Column([
                    name_field,
                    faculty_field,
                    dept_field,
                    spec_field,
                    email_field,
                    phone_field,
                    Row([
                        FilledButton("Mark Retired" if not p.is_retired else "Mark Active",
                                      bgcolor=Colors.RED_700 if not p.is_retired else ATBU_GREEN,
                                      color=Colors.WHITE,
                                      on_click=lambda _: self._toggle_retired(prof.id)),
                        FilledButton("💾 Save Changes", 
                                      bgcolor=ATBU_GREEN, color=Colors.WHITE,
                                      on_click=lambda _: self._save_edit(prof.id)),
                    ], spacing=12),
                ], tight=True, spacing=12, width=450),
                actions=[
                    OutlinedButton("Cancel", on_click=lambda e: close_dialog(self.page)),
                ],
            )
            show_dialog(self.page, dlg)
        finally:
            session.close()
    
    def _toggle_retired(self, prof_id):
        # Read professor name for confirmation dialog (quick session)
        session = get_session()
        try:
            p = session.get(Professor, prof_id)
            if not p:
                return
            prof_name = f"{p.last_name}, {p.first_name}"
            action = "mark as ACTIVE" if p.is_retired else "mark as RETIRED"
        finally:
            session.close()
        
        # Show confirmation (opens its own session in callback)
        def _confirm_yes(e):
            s = get_session()
            try:
                p = s.get(Professor, prof_id)
                if not p:
                    return
                p.is_retired = 1 if not p.is_retired else 0
                p.retirement_status = "Retirement" if p.is_retired else None
                p.updated_at = datetime.now(timezone.utc)
                s.commit()
                close_dialog(self.page)
                show_snack(self.page, f"✅ {p.last_name}, {p.first_name} {action}", duration=2000, bgcolor=ATBU_GREEN)
                self._refresh()
            finally:
                s.close()
        dlg = AlertDialog(
            title=Text(f"Confirm: {action.title()}?"),
            content=Text(f"Are you sure you want to {action}\n{prof_name}?"),
            actions=[
                OutlinedButton("Cancel", on_click=lambda e: close_dialog(self.page)),
                FilledButton("Confirm", on_click=_confirm_yes, bgcolor=ATBU_GREEN, color=Colors.WHITE),
            ],
        )
        show_dialog(self.page, dlg)
    
    def _save_edit(self, prof_id):
        """Save edited professor fields to database."""
        fields = getattr(self, '_edit_fields', None)
        if not fields:
            close_dialog(self.page)
            return
        
        session = get_session()
        try:
            p = session.get(Professor, prof_id)
            if not p:
                show_snack(self.page, "❌ Professor not found", bgcolor=Colors.RED_400)
                return
            
            # Update fields from the dialog
            p.faculty = fields["faculty"].value.strip() if fields["faculty"].value else p.faculty
            p.department = fields["dept"].value.strip() if fields["dept"].value else p.department
            p.area_of_specialization = fields["spec"].value.strip() if fields["spec"].value else p.area_of_specialization
            p.email = fields["email"].value.strip() if fields["email"].value else p.email
            p.updated_at = datetime.now(timezone.utc)
            
            # Update phone numbers
            phone_raw = fields["phone"].value if fields["phone"].value else ""
            from import_export import parse_phones
            new_phones = parse_phones(phone_raw)
            existing_phones = {pn.phone: pn for pn in p.phone_numbers}
            
            # Add new phones
            for i, phone in enumerate(new_phones):
                if phone not in existing_phones:
                    session.add(PhoneNumber(
                        professor_id=prof_id,
                        phone=phone,
                        is_primary=1 if i == 0 and not existing_phones else 0
                    ))
            
            # Remove phones no longer in the list
            for phone, pn in existing_phones.items():
                if phone not in new_phones:
                    session.delete(pn)
            
            session.commit()
            show_snack(self.page, f"✅ {p.last_name}, {p.first_name} updated successfully",
                       duration=2000, bgcolor=ATBU_GREEN)
        except Exception as ex:
            session.rollback()
            show_snack(self.page, f"❌ Save failed: {str(ex)}", bgcolor=Colors.RED_400)
        finally:
            session.close()
            self._edit_fields = {}
            close_dialog(self.page)
            self._refresh()
