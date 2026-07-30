"""
screens/settings.py — Settings screen with password change + config
ATBU Academic Planning Portal
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from flet import (
    Container, Column, Row, Text, Card, TextField, FilledButton, OutlinedButton,
    Padding, Margin, Colors,
    MainAxisAlignment, CrossAxisAlignment, FontWeight, AlertDialog,
    ScrollMode
)
from database import get_session, Professor, AppSetting, DB_PATH
from import_export import export_nuc_format
from ui_helpers import show_dialog, close_dialog, show_snack, save_file

ATBU_GREEN = "#00843D"
ATBU_GOLD = "#F5A623"
ATBU_DARK = "#1A1A2E"
ATBU_BG = "#F5F7FA"
ATBU_MUTED = "#6B7280"


class SettingsScreen:
    """Settings screen for password, config, and maintenance."""

    def __init__(self, app):
        self.app = app
        self.page = app.page

    def __call__(self):
        return self._build()

    def _build(self):
        # Current password fields
        self.current_pw = TextField(
            label="Current Password", password=True, 
            can_reveal_password=True, width=350
        )
        self.new_pw = TextField(
            label="New Password", password=True, 
            can_reveal_password=True, width=350,
            hint_text="Min 6 characters"
        )
        self.confirm_pw = TextField(
            label="Confirm New Password", password=True,
            can_reveal_password=True, width=350
        )
        
        return Container(
            content=Column([
                # Header
                Container(
                    content=Column([
                        Text("⚙️ Settings", size=28, weight=FontWeight.BOLD, 
                             color=ATBU_DARK),
                        Text("Configure application preferences and security", 
                             size=14, color=ATBU_MUTED),
                    ]),
                    margin=Margin.only(bottom=16),
                ),
                
                # Password Change Card
                Card(
                    content=Container(
                        content=Column([
                            Text("🔐 Change Password", size=18, 
                                 weight=FontWeight.BOLD, color=ATBU_DARK),
                            Text("Editing professor records requires the admin password.", 
                                 size=12, color=ATBU_MUTED),
                            Container(height=12),
                            self.current_pw,
                            self.new_pw,
                            self.confirm_pw,
                            Container(height=8),
                            FilledButton(
                                "Update Password",
                                on_click=self._change_password,
                                bgcolor=ATBU_GREEN, color=Colors.WHITE,
                                width=200,
                            ),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
                
                Container(height=16),
                
                # Database Info Card
                Card(
                    content=Container(
                        content=Column([
                            Text("🗄️ Database", size=18, 
                                 weight=FontWeight.BOLD, color=ATBU_DARK),
                            Container(height=8),
                            self._info_row("Location", DB_PATH),
                            self._info_row("Total Professors", str(self._get_count())),
                            self._info_row("Faculties", str(self._get_faculty_count())),
                            Container(height=8),
                            Row([
                                FilledButton(
                                    "📤 Export NUC Format", 
                                    on_click=self._do_export,
                                    bgcolor=ATBU_GREEN, color=Colors.WHITE,
                                ),
                                FilledButton(
                                    "💾 Backup Database", 
                                    on_click=self._backup_database,
                                    bgcolor="#2196F3", color=Colors.WHITE,
                                ),
                            ], spacing=12),
                            Container(height=8),
                            Row([
                                FilledButton(
                                    "🔓 Reset Password (emergency)",
                                    on_click=self._emergency_reset,
                                    bgcolor=Colors.RED_700, color=Colors.WHITE,
                                ),
                            ], spacing=12),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
                
            ], scroll=ScrollMode.AUTO),
        )
    
    def _info_row(self, label, value):
        return Container(
            content=Row([
                Text(label, size=13, weight=FontWeight.BOLD, 
                     color=ATBU_MUTED, width=200),
                Text(value, size=13, color=ATBU_DARK, selectable=True),
            ]),
            padding=Padding.symmetric(vertical=3),
        )
    
    def _get_count(self):
        session = get_session()
        count = session.query(Professor).count()
        session.close()
        return count
    
    def _get_faculty_count(self):
        session = get_session()
        count = session.query(Professor.faculty).distinct().count()
        session.close()
        return count
    
    def _change_password(self, e):
        """Change the admin password."""
        if not self.app.is_unlocked:
            self.app._show_password_dialog()
            return
        
        import bcrypt
        if not self.current_pw.value:
            show_snack(self.page, "Please enter current password", bgcolor=Colors.RED_400)
            return
        
        if not self.new_pw.value or len(self.new_pw.value) < 6:
            show_snack(self.page, "New password must be at least 6 characters", bgcolor=Colors.RED_400)
            return
        
        if self.new_pw.value != self.confirm_pw.value:
            show_snack(self.page, "New passwords do not match", bgcolor=Colors.RED_400)
            return
        
        # Verify current password
        session = get_session()
        stored = session.query(AppSetting).filter_by(key="password_hash").first()
        if stored and not bcrypt.checkpw(
            self.current_pw.value.encode('utf-8'),
            stored.value.encode('utf-8')
        ):
            show_snack(self.page, "❌ Current password is incorrect", bgcolor=Colors.RED_400)
            session.close()
            return
        
        # Update password
        hashed = bcrypt.hashpw(self.new_pw.value.encode('utf-8'), bcrypt.gensalt())
        stored.value = hashed.decode('utf-8')
        session.commit()
        session.close()
        
        # Clear fields
        self.current_pw.value = ""
        self.new_pw.value = ""
        self.confirm_pw.value = ""
        
        show_snack(self.page, "✅ Password updated successfully!", bgcolor=ATBU_GREEN, duration=2000)
    
    def _do_export(self, e):
        """Export the database to NUC format Excel."""
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "export_nuc_format.xlsx"
        )
        try:
            count = export_nuc_format(output_path)
            show_snack(self.page, f"✅ Exported {count} professors to: {output_path}",
                       bgcolor=ATBU_GREEN, duration=3000)
        except Exception as ex:
            show_snack(self.page, f"❌ Export failed: {str(ex)}", bgcolor=Colors.RED_400)
    
    def _backup_database(self, e):
        """Backup the database to a user-chosen location."""
        backup_path = save_file(
            title="Save Database Backup",
            default_name="professors_backup.db",
            filetypes=[("SQLite database", "*.db"), ("All files", "*.*")]
        )
        if not backup_path:
            return
        try:
            import shutil
            shutil.copy2(DB_PATH, backup_path)
            show_snack(self.page, f"✅ Database backed up to:\n{backup_path}",
                       bgcolor=ATBU_GREEN, duration=3000)
        except Exception as ex:
            show_snack(self.page, f"❌ Backup failed: {str(ex)}", bgcolor=Colors.RED_400)

    def _emergency_reset(self, e):
        """Emergency password reset (clears hash, restart app to set new one)."""
        dlg = AlertDialog(
            modal=True,
            title=Text("⚠️ Emergency Password Reset"),
            content=Text(
                "This will clear the stored password hash. "
                "On the next app launch, you will be prompted to set a new password.\n\n"
                "Are you sure?"
            ),
            actions=[
                OutlinedButton("Cancel", on_click=lambda e: close_dialog(self.page)),
                FilledButton("Reset", on_click=self._confirm_reset,
                             bgcolor=Colors.RED_700, color=Colors.WHITE),
            ],
        )
        show_dialog(self.page, dlg)
    
    def _confirm_reset(self, e):
        """Confirm emergency password reset."""
        session = get_session()
        setting = session.query(AppSetting).filter_by(key="password_hash").first()
        if setting:
            session.delete(setting)
            session.commit()
        session.close()
        
        close_dialog(self.page)
        self.app.password_set = False
        self.app.is_unlocked = False
        show_snack(self.page, "✅ Password reset. Restart the app to set a new password.",
                   bgcolor=ATBU_GOLD, duration=5000)
