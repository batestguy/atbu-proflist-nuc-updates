"""
main.py — ATBU Academic Planning Portal (Flet Desktop App)
Beautified with ATBU logo, gradients, polished design, fixed lock button.
"""

import os
import sys

import flet as ft
from flet import (
    Page, Container, Column, Row, Text, Icon, Image,
    AlertDialog, TextField, FilledButton, OutlinedButton,
    VerticalDivider, Padding, Margin, Border, BorderRadius, Colors, Theme, MainAxisAlignment,
    CrossAxisAlignment, ScrollMode, LinearGradient, Alignment,
    BoxShadow, Ref, FontWeight, TextAlign, BoxFit
)
import atbu_icons as icons


# ── Resource Path Helper (works with PyInstaller .exe) ──
def resource_path(relative_path):
    """
    Return the absolute path to a bundled resource.
    When running as PyInstaller .exe, files are extracted to a temp
    directory pointed to by sys._MEIPASS.
    When running as a Python script, paths are relative to this file.
    """
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


sys.path.insert(0, resource_path("."))
from database import init_db, get_session, AppSetting
from screens.dashboard import DashboardScreen
from screens.professors_list import ProfessorsListScreen
from screens.add_professor import AddProfessorScreen
from screens.about import AboutScreen
from screens.settings import SettingsScreen
from ui_helpers import show_dialog, close_dialog, show_snack

# ── ATBU Brand Colors ──
ATBU_GREEN = "#00843D"
ATBU_GREEN_DARK = "#006630"
ATBU_GREEN_LIGHT = "#00A84D"
ATBU_GOLD = "#F5A623"
ATBU_DARK = "#1A1A2E"
ATBU_BG = "#F0F2F5"
ATBU_MUTED = "#6B7280"
ATBU_WHITE = "#FFFFFF"
ATBU_SHADOW = "rgba(0, 0, 0, 0.08)"

LOGO_PATH = resource_path(os.path.join("assets", "atbu_logo.png"))


class AcademicPlanningApp:
    """Main application controller with beautified ATBU-branded UI."""

    def __init__(self, page: Page):
        self.page = page
        self.is_unlocked = False
        # self._lock_button_container removed (sidebar fully rebuilt instead)
        
        # Page setup
        self.page.title = "ATBU Academic Planning Portal"
        self.page.theme = Theme(color_scheme_seed=ATBU_GREEN, use_material3=True)
        self.page.bgcolor = ATBU_BG
        self.page.padding = 0
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.window_min_width = 1024
        self.page.window_min_height = 600
        
        init_db()
        self._check_password_setup()
        self._build_ui()

    def _check_password_setup(self):
        session = get_session()
        pw = session.query(AppSetting).filter_by(key="password_hash").first()
        session.close()
        self.password_set = pw is not None

    def _build_ui(self):
        """Build the beautified main interface."""
        self.selected_nav = 0

        # ── Sidebar ──
        # Build the expanded sidebar as a Container so we can rebuild it fully
        self.sidebar = self._build_sidebar()
        
        # ── Content Area ──
        self.content_area = Container(
            expand=True, bgcolor=ATBU_BG,
            padding=Padding.all(24),
        )

        # ── Password Fields ──
        self.password_field = TextField(
            password=True, can_reveal_password=True,
            hint_text="Enter password", width=300,
        )
        self._password_dialog = AlertDialog(
            modal=True,
            title=Text("🔒 Password Required"),
            content=Column([
                Text("Enter the admin password to unlock editing:"),
                self.password_field,
            ], tight=True, spacing=10),
            actions=[
                OutlinedButton("Cancel", on_click=self._close_dialog),
                FilledButton("Unlock", on_click=self._verify_password,
                    bgcolor=ATBU_GREEN, color=Colors.WHITE),
            ],
        )

        self.setup_pw1 = TextField(
            password=True, can_reveal_password=True,
            hint_text="New password (min 6 characters)", width=300,
        )
        self.setup_pw2 = TextField(
            password=True, can_reveal_password=True,
            hint_text="Confirm password", width=300,
        )
        self._setup_dialog = AlertDialog(
            modal=True, title=Text("🔐 Set Administrator Password"),
            content=Column([
                Text("First-time setup: Create the admin password.", size=13),
                self.setup_pw1, self.setup_pw2,
            ], tight=True, spacing=10),
            actions=[
                FilledButton("Set Password", on_click=self._set_password,
                    bgcolor=ATBU_GREEN, color=Colors.WHITE),
            ],
        )

        # ── Main Layout ──
        self.main_layout = Row([
            self.sidebar,
            VerticalDivider(width=1, color=Colors.GREY_300),
            self.content_area,
        ], expand=True, spacing=0)

        self.page.add(self.main_layout)

        if not self.password_set:
            show_dialog(self.page, self._setup_dialog)

        self._load_screen(0)

    def _build_sidebar(self):
        """Build the sidebar with ATBU logo, custom nav, and lock button."""
        lock_icon = icons.LOCK_OPEN if self.is_unlocked else icons.LOCK_OUTLINE
        lock_color = ATBU_GREEN if self.is_unlocked else ATBU_MUTED
        lock_label = "Editing: On" if self.is_unlocked else "Editing: Off"

        # Check if logo exists
        has_logo = os.path.exists(LOGO_PATH)
        if not has_logo:
            print(f"[ATBU] WARNING: Logo not found at {LOGO_PATH}")

        # ── Custom Navigation Items (reliable across all Flet versions) ──
        nav_labels = ["Dashboard", "All Professors", "Add Professor",
                      "Import / Export", "About", "Settings"]
        nav_icons_unsel = [icons.DASHBOARD_ROUNDED, icons.PEOPLE_OUTLINE_ROUNDED,
                          icons.PERSON_ADD_OUTLINED, icons.FILE_DOWNLOAD_OUTLINED,
                          icons.INFO_OUTLINE_ROUNDED, icons.SETTINGS_OUTLINED]
        nav_icons_sel = [icons.DASHBOARD, icons.PEOPLE, icons.PERSON_ADD,
                        icons.FILE_DOWNLOAD, icons.INFO, icons.SETTINGS]

        nav_buttons = []
        for i, (label, icon_u, icon_s) in enumerate(
            zip(nav_labels, nav_icons_unsel, nav_icons_sel)):
            is_selected = (self.selected_nav == i)
            bg = Colors.with_opacity(0.1, ATBU_GREEN) if is_selected else "transparent"
            txt_color = ATBU_GREEN if is_selected else ATBU_DARK
            icon_color = ATBU_GREEN if is_selected else ATBU_MUTED
            cur_icon = icon_s if is_selected else icon_u
            nav_buttons.append(
                Container(
                    content=Row([
                        Icon(cur_icon, size=22, color=icon_color),
                        Text(label, size=13, weight=FontWeight.BOLD if is_selected else FontWeight.NORMAL,
                             color=txt_color),
                    ], spacing=12, alignment=MainAxisAlignment.START),
                    on_click=lambda e, idx=i: self._on_nav_click(idx),
                    bgcolor=bg,
                    border_radius=BorderRadius.all(8),
                    padding=Padding.symmetric(vertical=10, horizontal=16),
                    margin=Margin.symmetric(horizontal=8, vertical=2),

                )
            )

        return Container(
            width=230,
            bgcolor=Colors.WHITE,
            content=Column([
                # ── Brand Header ──
                Container(
                    content=Column([
                        # Logo
                        Container(
                            content=(
                                Image(src=LOGO_PATH, width=80, height=80, fit=BoxFit.CONTAIN)
                                if has_logo
                                else Container(
                                    content=Text("🏛️", size=40),
                                    alignment=Alignment.CENTER,
                                )
                            ),
                            alignment=Alignment.CENTER,
                            margin=Margin.only(top=16, bottom=4),
                        ),
                        # University Name
                        Text("ATBU", size=20, weight=FontWeight.BOLD,
                            color=ATBU_GREEN, text_align=TextAlign.CENTER),
                        Text("Academic Planning", size=12, color=ATBU_MUTED,
                            text_align=TextAlign.CENTER),
                        Text("Doctrina Mater Artium", size=9, color=ATBU_GOLD,
                            italic=True,
                            text_align=TextAlign.CENTER),
                    ], horizontal_alignment=CrossAxisAlignment.CENTER, spacing=1),
                    padding=Padding.only(bottom=8),
                ),

                # ── Custom Navigation Items ──
                Container(
                    content=Column(nav_buttons, spacing=0),
                    expand=True,
                ),

                # ── Unlock Button (visible when locked) ──
                *([Container(
                    content=FilledButton(
                        "🔓 Unlock Editing",
                        on_click=self._show_password_dialog,
                        bgcolor=ATBU_GREEN, color=Colors.WHITE,
                        width=200, height=40,
                    ),
                    alignment=Alignment.CENTER,
                    padding=Padding.symmetric(vertical=8, horizontal=10),
                )] if not self.is_unlocked else []),

                # ── Lock Status Footer (click to lock when unlocked) ──
                Container(
                    content=Row([
                        Icon(lock_icon, size=18, color=lock_color),
                        Text(lock_label, size=12, color=lock_color,
                            weight=FontWeight.BOLD),
                    ], alignment=MainAxisAlignment.CENTER, spacing=6),
                    on_click=self._toggle_lock,
                    bgcolor=Colors.GREY_100 if not self.is_unlocked else Colors.with_opacity(0.1, ATBU_GREEN),
                    border_radius=BorderRadius.all(8),
                    padding=Padding.symmetric(vertical=10, horizontal=16),
                    margin=Margin.all(12),
                ),

                # ── Footer ──
                Container(
                    content=Text("© 2026 DAP, ATBU", size=9, color=ATBU_MUTED,
                        text_align=TextAlign.CENTER),
                    padding=Padding.all(8),
                ),
            ], spacing=0),
        )

    def _rebuild_sidebar(self):
        """Full rebuild of the sidebar to reflect lock state changes."""
        new_sidebar = self._build_sidebar()
        self.main_layout.controls[0] = new_sidebar
        self.sidebar = new_sidebar
        self._load_screen(self.selected_nav)
        self.page.update()

    def _toggle_lock(self, e):
        if self.is_unlocked:
            self.is_unlocked = False
            self._rebuild_sidebar()
            show_snack(self.page, "🔒 Editing locked", duration=1500)
        else:
            self._show_password_dialog()

    def _show_password_dialog(self):
        self.password_field.value = ""
        show_dialog(self.page, self._password_dialog)

    def _verify_password(self, e):
        entered = self.password_field.value
        if not entered:
            show_snack(self.page, "Please enter a password", bgcolor=Colors.RED_400)
            return
        import bcrypt
        session = get_session()
        stored = session.query(AppSetting).filter_by(key="password_hash").first()
        session.close()
        if stored and bcrypt.checkpw(entered.encode('utf-8'), stored.value.encode('utf-8')):
            self.is_unlocked = True
            close_dialog(self.page)
            self._rebuild_sidebar()
            show_snack(self.page, "🔓 Editing unlocked!", duration=2000, bgcolor=ATBU_GREEN)
        else:
            show_snack(self.page, "❌ Incorrect password", bgcolor=Colors.RED_400)

    def _set_password(self, e):
        pw1, pw2 = self.setup_pw1.value, self.setup_pw2.value
        if not pw1 or len(pw1) < 6:
            show_snack(self.page, "Password must be at least 6 characters", bgcolor=Colors.RED_400)
            return
        if pw1 != pw2:
            show_snack(self.page, "Passwords do not match", bgcolor=Colors.RED_400)
            return
        import bcrypt
        hashed = bcrypt.hashpw(pw1.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        session = get_session()
        setting = session.query(AppSetting).filter_by(key="password_hash").first()
        if not setting:
            setting = AppSetting(key="password_hash", value=hashed)
            session.add(setting)
        else:
            setting.value = hashed
        session.commit()
        session.close()
        self.password_set = True
        self.is_unlocked = True
        close_dialog(self.page)
        self._rebuild_sidebar()
        show_snack(self.page, "✅ Password set! Editing is now unlocked.",
                   duration=3000, bgcolor=ATBU_GREEN)

    def _close_dialog(self, e):
        close_dialog(self.page)

    def _on_nav_click(self, index):
        """Handle custom nav button click."""
        self.selected_nav = index
        self._rebuild_sidebar()  # Rebuilds nav highlighting + loads screen



    def _load_screen(self, index):
        screen_names = ["Dashboard", "Professors", "Add Professor", "Import/Export", "About", "Settings"]
        screen_name = screen_names[index] if index < len(screen_names) else f"Index {index}"
        
        screens = [
            lambda: DashboardScreen(self),
            lambda: ProfessorsListScreen(self),
            lambda: AddProfessorScreen(self),
            lambda: ImportExportScreen(self),
            lambda: AboutScreen(self),
            lambda: SettingsScreen(self),
        ]
        if 0 <= index < len(screens):
            try:
                print(f"[ATBU] Loading screen: {screen_name} (index={index})")
                screen = screens[index]()
                print(f"[ATBU] Screen instance created: {type(screen).__name__}")
                content = screen() if callable(screen) else screen
                print(f"[ATBU] Screen content built: {type(content).__name__}")
                self.content_area.content = content
                self.page.update()
                print(f"[ATBU] Screen loaded OK: {screen_name}")
            except Exception as ex:
                import traceback
                tb = traceback.format_exc()
                print(f"[ATBU] ERROR loading {screen_name}: {type(ex).__name__}: {ex}")
                print(tb)
                self.content_area.content = Container(
                    content=Column([
                        Text(f"⚠️ {screen_name} Error", size=20, weight=FontWeight.BOLD, color=Colors.RED_400),
                        Text(f"{type(ex).__name__}: {ex}", size=12, color=Colors.RED_400),
                        Text(tb[-800:], size=10, color=Colors.GREY_600, selectable=True),
                    ]),
                    padding=Padding.all(24),
                )
                self.page.update()


class ImportExportScreen:
    """Inline Import/Export screen to avoid circular imports."""
    def __init__(self, app):
        self.app = app
        self.page = app.page
    def __call__(self):
        from screens.import_export_screen import ImportExportScreen as IES
        return IES(self.app)()


def main(page: Page):
    AcademicPlanningApp(page)


def setup_flet_view():
    """
    Find a bundled Flet desktop engine (flet.exe) to avoid internet
    download on first launch.

    Checks:
    1. Inside PyInstaller onefile bundle via resource_path()
    2. Next to the .exe or script file (portable folder mode)

    If found, sets FLET_VIEW_PATH so flet_desktop skips the download.
    """
    # 1. Bundled inside PyInstaller --onefile .exe
    candidate = resource_path(os.path.join("flet_view", "flet"))
    if os.path.isfile(os.path.join(candidate, "flet.exe")):
        os.environ["FLET_VIEW_PATH"] = candidate
        return

    # 2. 'flet_view' folder next to the .exe or script (portable setup)
    base = os.path.dirname(
        sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    )
    candidate = os.path.join(base, "flet_view", "flet")
    if os.path.isfile(os.path.join(candidate, "flet.exe")):
        os.environ["FLET_VIEW_PATH"] = candidate


if __name__ == "__main__":
    setup_flet_view()  # Must run BEFORE ft.run()
    ft.run(main=main)
