"""
screens/import_export_screen.py — Import/Export screen with file picker
ATBU Academic Planning Portal
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from flet import (
    Container, Column, Row, Text, Card, FilledButton, OutlinedButton,
    Padding, Margin, Colors, FontWeight, CrossAxisAlignment,
    ScrollMode
)
import atbu_icons as icons
from database import get_session, Professor, ImportHistory
from import_export import import_excel, export_nuc_format
from ui_helpers import show_snack, pick_file, save_file

ATBU_GREEN = "#00843D"
ATBU_GOLD = "#F5A623"
ATBU_DARK = "#1A1A2E"
ATBU_MUTED = "#6B7280"


class ImportExportScreen:
    """Screen for importing and exporting professor data in NUC formats."""

    def __init__(self, app):
        self.app = app
        self.page = app.page

    def __call__(self):
        return self._build()

    def _build(self):
        import_history = self._get_import_history()
        
        return Container(
            content=Column([
                # Header
                Container(
                    content=Column([
                        Text("📂 Import / Export", size=28, weight=FontWeight.BOLD, 
                             color=ATBU_DARK),
                        Text("Import Excel files or export data in NUC format", 
                             size=14, color=ATBU_MUTED),
                    ]),
                    margin=Margin.only(bottom=16),
                ),
                
                # Import Card
                Card(
                    content=Container(
                        content=Column([
                            Text("📥 Import Excel", size=18, weight=FontWeight.BOLD, 
                                 color=ATBU_DARK),
                            Text(
                                "Upload a .xlsx file in either NUC format or "
                                "Newly Promoted format. The system auto-detects "
                                "the format and imports the data. Duplicates are "
                                "automatically updated.",
                                size=12, color=ATBU_MUTED,
                            ),
                            Container(height=12),
                            FilledButton(
                                "📤 Select & Import Excel File",
                                icon=icons.UPLOAD_FILE,
                                on_click=self._do_import,
                                bgcolor=ATBU_GREEN, color=Colors.WHITE,
                                width=280, height=44,
                                disabled=not self.app.is_unlocked,
                            ),
                            Container(height=8),
                            Text(
                                "🔒 Import requires editing to be unlocked" 
                                if not self.app.is_unlocked else "",
                                size=11, color=ATBU_GOLD,
                            ),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
                
                Container(height=16),
                
                # Export Card
                Card(
                    content=Container(
                        content=Column([
                            Text("📤 Export NUC Format", size=18, 
                                 weight=FontWeight.BOLD, color=ATBU_DARK),
                            Text(
                                "Export the full professors database in the official "
                                "NUC format (.xlsx) ready for submission. Includes "
                                "ATBU branding and Directorate attribution.",
                                size=12, color=ATBU_MUTED,
                            ),
                            Container(height=12),
                            Row([
                                FilledButton(
                                    "💾 Export to Default Location",
                                    icon=icons.FILE_DOWNLOAD,
                                    on_click=self._export_default,
                                    bgcolor=ATBU_GREEN, color=Colors.WHITE,
                                    width=250,
                                ),
                                FilledButton(
                                    "📁 Export to Custom Location",
                                    icon=icons.FOLDER_OPEN,
                                    on_click=self._do_custom_export,
                                    bgcolor=Colors.BLUE_700, color=Colors.WHITE,
                                    width=250,
                                ),
                            ], spacing=12),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
                
                Container(height=16),
                
                # Import History Card
                Card(
                    content=Container(
                        content=Column([
                            Text("📋 Import History", size=18, 
                                 weight=FontWeight.BOLD, color=ATBU_DARK),
                            Container(height=8),
                            *([_history_row(h) for h in import_history] 
                              if import_history else [
                                Text("No imports yet", size=13, color=ATBU_MUTED, 
                                     italic=True)
                              ]),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
                

            ], scroll=ScrollMode.AUTO),
        )
    
    def _get_import_history(self):
        session = get_session()
        history = session.query(ImportHistory).order_by(
            ImportHistory.imported_at.desc()).limit(10).all()
        session.close()
        return history
    
    def _do_import(self, e=None):
        """Pick an Excel file and import it using tkinter filedialog."""
        filepath = pick_file(title="Select Excel file to import")
        if not filepath:
            return
        show_snack(self.page, f"⏳ Importing: {os.path.basename(filepath)}...")
        try:
            import_result = import_excel(filepath)
            show_snack(self.page, f"✅ Import complete: {import_result['added']} added, "
                       f"{import_result['updated']} updated, {import_result['skipped']} skipped",
                       bgcolor=ATBU_GREEN, duration=4000)
            self.app._load_screen(3)
        except Exception as ex:
            show_snack(self.page, f"❌ Import failed: {str(ex)}", bgcolor=Colors.RED_400, duration=5000)
        self.page.update()

    def _do_custom_export(self, e=None):
        """Pick a save location and export using tkinter filedialog."""
        output_path = save_file(
            title="Save NUC Export",
            default_name="ATBU_Full_Professors_List.xlsx"
        )
        if not output_path:
            return
        if not output_path.endswith('.xlsx'):
            output_path += '.xlsx'
        self._do_export(output_path)
    
    def _export_default(self, e):
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "export_nuc_format.xlsx"
        )
        self._do_export(output_path)
    
    def _do_export(self, output_path):
        try:
            count = export_nuc_format(output_path)
            show_snack(self.page, f"✅ Exported {count} professors to:\n{output_path}",
                       bgcolor=ATBU_GREEN, duration=4000)
        except Exception as ex:
            show_snack(self.page, f"❌ Export failed: {str(ex)}", bgcolor=Colors.RED_400)


def _history_row(h):
    return Container(
        content=Row([
            Text(f"📄 {h.filename}", size=12, weight=FontWeight.BOLD, 
                 color=ATBU_DARK, expand=True),
            Text(f"+{h.records_added} ~{h.records_updated} -{h.records_skipped}", 
                 size=12, color=ATBU_MUTED),
            Text(h.imported_at.strftime("%Y-%m-%d %H:%M"), 
                 size=11, color=ATBU_MUTED),
        ]),
        padding=Padding.symmetric(vertical=4),
        border=ft.Border(
            bottom=ft.BorderSide(0.5, Colors.GREY_300)
        ),
    )
