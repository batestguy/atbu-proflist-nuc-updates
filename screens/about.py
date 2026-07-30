"""
screens/about.py — About page with Abdulkadir Ahmed profile + ATBU branding + NUC accreditation
ATBU Academic Planning Portal
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from flet import (
    Container, Column, Row, Text, Card,
    Padding, Margin, Colors,
    MainAxisAlignment, CrossAxisAlignment, FontWeight,
    ScrollMode, Alignment
)

ATBU_GREEN = "#00843D"
ATBU_GOLD = "#F5A623"
ATBU_DARK = "#1A1A2E"
ATBU_BG = "#F5F7FA"
ATBU_MUTED = "#6B7280"


class AboutScreen:
    """About screen showing Director's profile, app purpose, and ATBU branding."""

    def __init__(self, app):
        self.app = app
        self.page = app.page

    def __call__(self):
        return self._build()

    def _build(self):
        return Container(
            content=Column([
                # Header
                Container(
                    content=Column([
                        Text("ℹ️ About", size=28, weight=FontWeight.BOLD, 
                             color=ATBU_DARK),
                        Text("The ATBU Academic Planning Portal", 
                             size=14, color=ATBU_MUTED),
                    ]),
                    margin=Margin.only(bottom=16),
                ),
                
                # ═══════════════════════════════════════
                # INNOVATION CREDIT - Prominent Section
                # ═══════════════════════════════════════
                Card(
                    content=Container(
                        content=Column([
                            # Innovation badge
                            Container(
                                content=Text("🏆 INNOVATION", size=11, 
                                           color=Colors.WHITE, weight=FontWeight.BOLD),
                                bgcolor=ATBU_GREEN,
                                padding=Padding.symmetric(vertical=4, horizontal=12),
                                border_radius=4,
                            ),
                            Container(height=12),
                            Text("ATBU Academic Planning Portal", size=22,
                                 weight=FontWeight.BOLD, color=ATBU_DARK),
                            Container(height=4),
                            Text(
                                "Conceptualized, Designed, and Developed under the leadership of",
                                size=13, color=ATBU_MUTED,
                            ),
                            Container(height=4),
                            Text("Prof. Abdulkadir Ahmed", size=24,
                                 weight=FontWeight.BOLD, color=ATBU_GREEN),
                            Text("Director of Academic Planning", size=14,
                                 color=ATBU_GOLD, weight=FontWeight.BOLD),
                            Text("Abubakar Tafawa Balewa University (ATBU), Bauchi",
                                 size=13, color=ATBU_MUTED),
                            Container(height=12),
                            Text(
                                "This application represents a transformative innovation in "
                                "academic data management at ATBU. It replaces outdated manual "
                                "processes with a modern, digital system that ensures accuracy, "
                                "accessibility, and accountability in the management of "
                                "professorial records.",
                                size=12, color=ATBU_DARK, italic=True,
                            ),
                        ], horizontal_alignment=CrossAxisAlignment.CENTER),
                        padding=Padding.all(24),
                    ),
                    elevation=3,
                ),
                
                Container(height=16),
                
                # ═══════════════════════════════════════
                # NUC ACCREDITATION IMPORTANCE Section
                # ═══════════════════════════════════════
                Card(
                    content=Container(
                        content=Column([
                            Row([
                                Container(
                                    content=Text("🎓", size=32),
                                    width=60, height=60,
                                    alignment=Alignment.CENTER,
                                ),
                                Container(
                                    content=Column([
                                        Text("NUC Accreditation Support", size=18,
                                             weight=FontWeight.BOLD, color=ATBU_DARK),
                                        Text("National Universities Commission Compliance",
                                             size=12, color=ATBU_MUTED),
                                    ]),
                                    expand=True,
                                    padding=Padding.only(left=12),
                                ),
                            ]),
                            Container(height=12),
                            Text(
                                "The National Universities Commission (NUC) requires all "
                                "Nigerian universities to maintain accurate and up-to-date "
                                "records of their academic staff, particularly Full Professors. "
                                "This data is critical for:",
                                size=12, color=ATBU_DARK,
                            ),
                            Container(height=8),
                            _bullet_point("Accreditation visits — instant access to complete professor profiles"),
                            _bullet_point("Resource verification — demonstrate staffing adequacy for each program"),
                            _bullet_point("Annual reporting — generate NUC-format returns in minutes instead of days"),
                            _bullet_point("Promotion tracking — monitor newly promoted and retiring professors year by year"),
                            _bullet_point("Data integrity — eliminate errors from manual Excel-based record keeping"),
                            Container(height=8),
                            Text(
                                "By digitizing and formalizing the professors database, this portal "
                                "ensures ATBU is always prepared for NUC accreditation exercises and "
                                "can produce verified, NUC-compliant reports at any time.",
                                size=12, color=ATBU_DARK, italic=True,
                            ),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
                
                Container(height=16),
                
                # ═══════════════════════════════════════
                # Director's Profile Card
                # ═══════════════════════════════════════
                Card(
                    content=Container(
                        content=Row([
                            # Photo placeholder (ATBU green circle with initials)
                            Container(
                                content=Text("AA", size=36, weight=FontWeight.BOLD, 
                                           color=Colors.WHITE),
                                width=120, height=120,
                                bgcolor=ATBU_GREEN,
                                border_radius=60,
                                alignment=Alignment.CENTER,
                            ),
                            # Details
                            Container(
                                content=Column([
                                    Text("Abdulkadir Ahmed", size=22, 
                                         weight=FontWeight.BOLD, color=ATBU_DARK),
                                    Text("Director of Academic Planning", size=14, 
                                         color=ATBU_GOLD, weight=FontWeight.BOLD),
                                    Text("Abubakar Tafawa Balewa University (ATBU), Bauchi", 
                                         size=13, color=ATBU_MUTED),
                                    Container(height=8),
                                    Text(
                                        "This application was conceptualized and developed under "
                                        "the leadership of Abdulkadir Ahmed to modernize the "
                                        "academic planning process at ATBU. It replaces manual "
                                        "Excel-based professor tracking with a formalized, "
                                        "searchable database that handles new entries, promotions, "
                                        "retirements, and NUC-mandated reporting.",
                                        size=12, color=ATBU_DARK, italic=True,
                                    ),
                                    Container(height=8),
                                    Text(
                                        "The portal provides real-time analytics, automated "
                                        "NUC-format exports, and a user-friendly interface for "
                                        "managing the university's full professors database.",
                                        size=12, color=ATBU_DARK,
                                    ),
                                ]),
                                expand=True,
                                padding=Padding.only(left=16),
                            ),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
                
                Container(height=16),
                
                # ═══════════════════════════════════════
                # ATBU Branding Card
                # ═══════════════════════════════════════
                Card(
                    content=Container(
                        content=Row([
                            # Logo placeholder
                            Container(
                                content=Text("🏛️", size=48),
                                width=100, height=100,
                                alignment=Alignment.CENTER,
                            ),
                            Container(
                                content=Column([
                                    Text("Abubakar Tafawa Balewa University", size=20, 
                                         weight=FontWeight.BOLD, color=ATBU_GREEN),
                                    Text("Doctrina Mater Artium", size=14, 
                                         color=ATBU_GOLD, weight=FontWeight.BOLD),
                                    Text("Education is the mother of the practical arts", 
                                         size=12, color=ATBU_MUTED, italic=True),
                                    Container(height=8),
                                    Text(
                                        "The ATBU Academic Planning Portal is an innovation by "
                                        "the Directorate of Academic Planning, designed to "
                                        "streamline the management of professorial records, "
                                        "facilitate NUC reporting, and provide data-driven "
                                        "insights for strategic academic planning at ATBU, Bauchi.",
                                        size=12, color=ATBU_DARK,
                                    ),
                                ]),
                                expand=True,
                                padding=Padding.only(left=16),
                            ),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
                
                Container(height=16),
                
                # ═══════════════════════════════════════
                # App Info Card
                # ═══════════════════════════════════════
                Card(
                    content=Container(
                        content=Column([
                            Text("📱 Application Information", size=16, 
                                 weight=FontWeight.BOLD, color=ATBU_DARK),
                            Container(height=8),
                            _info_row("Version", "1.1.0 (Desktop)"),
                            _info_row("Technology", "Python + Flet + SQLite"),
                            _info_row("Database", f"{self._get_db_stats()} professors"),
                            _info_row("Last Updated", "2026-07-30"),
                            _info_row("Developer", "Directorate of Academic Planning, ATBU"),
                        ]),
                        padding=Padding.all(24),
                    ),
                    elevation=2,
                ),
            ], scroll=ScrollMode.AUTO),
        )
    
    def _get_db_stats(self):
        from database import get_session, Professor
        session = get_session()
        count = session.query(Professor).count()
        session.close()
        return str(count)


def _info_row(label, value):
    return Container(
        content=Row([
            Text(label, size=13, weight=FontWeight.BOLD, color=ATBU_MUTED, width=150),
            Text(value, size=13, color=ATBU_DARK),
        ]),
        padding=Padding.symmetric(vertical=4),
    )


def _bullet_point(text):
    return Row([
        Container(
            content=Text("•", size=14, color=ATBU_GREEN, weight=FontWeight.BOLD),
            width=20,
            alignment=Alignment.CENTER,
        ),
        Text(text, size=12, color=ATBU_DARK, expand=True),
    ], spacing=4)
