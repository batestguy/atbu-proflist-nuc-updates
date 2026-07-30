"""
screens/dashboard.py — Dashboard with stats cards + Flet native charts
ATBU Academic Planning Portal
"""

import os
import sys
from collections import Counter
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from flet import (
    Container, Column, Row, Text, Card, Icon,
    Padding, Margin, BorderRadius, Colors,
    MainAxisAlignment, CrossAxisAlignment, FontWeight,
    ScrollMode, Alignment, TextAlign, TextOverflow
)
from database import get_session, Professor, PhoneNumber

ATBU_GREEN = "#00843D"
ATBU_GOLD = "#F5A623"
ATBU_DARK = "#1A1A2E"
ATBU_BG = "#F5F7FA"
ATBU_MUTED = "#6B7280"


class DashboardScreen:
    """Dashboard with summary stats, faculty/department/year charts."""

    def __init__(self, app):
        self.app = app
        self.page = app.page
        
    def __call__(self):
        return self._build()
    
    def _build(self):
        """Build the dashboard layout."""
        session = get_session()
        
        # ---- Summary Stats ----
        total = session.query(Professor).count()
        active = session.query(Professor).filter_by(is_retired=0).count()
        retired = session.query(Professor).filter(Professor.is_retired == 1).count()
        depts = session.query(Professor.department).distinct().count()
        faculties = session.query(Professor.faculty).distinct().count()
        total_phones = session.query(PhoneNumber).count()
        
        stats_cards = Row([
            self._stat_card("🏛️", "Total Professors", str(total), ATBU_GREEN),
            self._stat_card("✅", "Active", str(active), "#2196F3"),
            self._stat_card("📅", "Retired", str(retired), ATBU_MUTED),
            self._stat_card("🏢", "Faculties", str(faculties), ATBU_GOLD),
            self._stat_card("📚", "Departments", str(depts), "#9C27B0"),
            self._stat_card("📞", "Phone Numbers", str(total_phones), "#00BCD4"),
        ], wrap=True, spacing=12, run_spacing=12)
        
        # ---- Charts ----
        # Faculty distribution
        faculty_data = self._get_faculty_data(session)
        faculty_chart = self._build_bar_chart(
            "Professors by Faculty", faculty_data, ATBU_GREEN
        )
        
        # Department distribution (top 10)
        dept_data = self._get_dept_data(session, top_n=10)
        dept_chart = self._build_bar_chart(
            "Top 10 Departments", dept_data, "#2196F3"
        )
        
        # Gender distribution (from data that has SEX)
        gender_data = self._get_gender_data(session)
        gender_chart = self._build_pie_chart(
            "Professors by Gender", gender_data
        )
        
        # Year distribution
        year_data = self._get_year_data(session)
        year_chart = self._build_bar_chart(
            "Professors by Year of Appointment", year_data, ATBU_GOLD
        )
        
        # Specializations (top 8)
        spec_data = self._get_spec_data(session, top_n=8)
        spec_chart = self._build_bar_chart(
            "Top 8 Specializations", spec_data, "#9C27B0"
        )
        
        # Active vs Retired
        status_data = [("Active", active), ("Retired", retired)]
        status_chart = self._build_pie_chart(
            "Active vs Retired", status_data
        )
        
        session.close()
        
        # Layout
        content = Column([
            # Header
            Container(
                content=Column([
                    Text("📊 Dashboard", size=28, weight=FontWeight.BOLD, 
                         color=ATBU_DARK),
                    Text("Academic Planning Overview", size=14, color=ATBU_MUTED),
                ]),
                margin=Margin.only(bottom=16),
            ),
            # Stats cards
            stats_cards,
            Container(height=16),
            # Charts row 1: Faculty + Gender
            Row([
                Container(content=faculty_chart, expand=True,                padding=Padding.all(8),
                         height=320),
                Container(content=gender_chart, expand=True,
                         padding=8, height=320),
            ], spacing=12),
            # Charts row 2: Departments + Year
            Row([
                Container(content=dept_chart, expand=True,
                         padding=8, height=320),
                Container(content=year_chart, expand=True,
                         padding=8, height=320),
            ], spacing=12),
            # Charts row 3: Specializations + Status
            Row([
                Container(content=spec_chart, expand=True,
                         padding=8, height=320),
                Container(content=status_chart, expand=True,
                         padding=8, height=320),
            ], spacing=12),
        ], scroll=ScrollMode.AUTO)
        
        return Container(content=content)
    
    def _stat_card(self, icon, label, value, color):
        """Build a single summary stat card."""
        return Card(
            content=Container(
                content=Column([
                    Text(icon, size=28),
                    Text(value, size=28, weight=FontWeight.BOLD, color=color),
                    Text(label, size=12, color=ATBU_MUTED),
                ], horizontal_alignment=CrossAxisAlignment.CENTER, 
                   spacing=4, tight=True),
                padding=Padding.all(16),
                width=160,
            ),
            elevation=2,
        )
    
    def _get_faculty_data(self, session):
        """Get faculty counts using GROUP BY (single query)."""
        from sqlalchemy import func
        rows = session.query(
            Professor.faculty, func.count(Professor.id).label('count')
        ).filter(Professor.faculty != ""
        ).group_by(Professor.faculty
        ).order_by(func.count(Professor.id).desc()).all()
        result = []
        for faculty, count in rows:
            short = faculty[:30] + ".." if len(faculty) > 30 else faculty
            result.append((short, count))
        return result
    
    def _get_dept_data(self, session, top_n=10):
        """Get top N departments by count."""
        from sqlalchemy import func
        depts = session.query(
            Professor.department, func.count(Professor.id).label('count')
        ).group_by(Professor.department).order_by(func.count(Professor.id).desc()
        ).limit(top_n).all()
        return [(d[0][:25] + ".." if len(d[0]) > 25 else d[0], d.count) 
                for d in depts]
    
    def _get_gender_data(self, session):
        """Get gender distribution (from records with SEX filled)."""
        male = session.query(Professor).filter(
            Professor.sex.ilike("M")
        ).count()
        female = session.query(Professor).filter(
            Professor.sex.ilike("F")
        ).count()
        total = session.query(Professor).count()
        known = male + female
        result = []
        if male: result.append(("Male", male))
        if female: result.append(("Female", female))
        if known < total:
            result.append((f"Data pending ({known}/{total})", total - known))
        return result
    
    def _get_year_data(self, session):
        """Get yearly appointment counts."""
        from sqlalchemy import func
        years = session.query(
            Professor.added_year, func.count(Professor.id)
        ).filter(Professor.added_year.isnot(None)
        ).group_by(Professor.added_year
        ).order_by(Professor.added_year).all()
        return [(str(y), c) for y, c in years]
    
    def _get_spec_data(self, session, top_n=8):
        """Get top N specializations."""
        from sqlalchemy import func
        specs = session.query(
            Professor.area_of_specialization, 
            func.count(Professor.id).label('count')
        ).group_by(Professor.area_of_specialization
        ).order_by(func.count(Professor.id).desc()
        ).limit(top_n).all()
        return [(s[0][:25] + ".." if len(s[0]) > 25 else s[0], s.count) 
                for s in specs]
    
    def _build_bar_chart(self, title, data, bar_color):
        """Build a bar chart using Container-based visualizations.
        Bars all share the same baseline for proper alignment.
        """
        if not data:
            return Container(
                content=Text("No data available", italic=True, color=ATBU_MUTED),
                padding=Padding.all(16),
            )
        
        max_val = max(v for _, v in data) if data else 1
        show_data = data[:15]
        bar_max_height = 160
        label_width = 80
        
        # Build each bar: value on top, bar in middle, label at bottom
        # Use a fixed-height Container per bar so baselines align
        bar_columns = []
        for label, value in show_data:
            pct = value / max_val if max_val > 0 else 0
            bar_height = max(4, int(pct * bar_max_height))
            spacer_height = bar_max_height - bar_height
            
            bar_columns.append(
                Container(
                    content=Column([
                        # Value label on top
                        Text(str(value), size=10, weight=FontWeight.BOLD,
                             color=bar_color, text_align=TextAlign.CENTER,
                             width=label_width),
                        # Spacer to push bar down so all bars share same baseline
                        Container(height=spacer_height),
                        # The bar itself
                        Container(
                            width=24,
                            height=bar_height,
                            bgcolor=bar_color,
                            border_radius=BorderRadius.only(
                                top_left=3, top_right=3,
                                bottom_left=0, bottom_right=0
                            ),
                        ),
                        # Label below bar (fixed height box)
                        Container(
                            content=Text(label, size=8, color=ATBU_MUTED,
                                        text_align=TextAlign.CENTER,
                                        no_wrap=False,
                                        max_lines=2,
                                        overflow=TextOverflow.ELLIPSIS),
                            width=label_width,
                            height=28,
                            alignment=Alignment.TOP_CENTER,
                        ),
                    ], horizontal_alignment=CrossAxisAlignment.CENTER,
                       spacing=2, tight=True),
                    padding=Padding.only(right=6),
                )
            )
        
        chart = Container(
            content=Row(
                bar_columns,
                alignment=MainAxisAlignment.START,
                vertical_alignment=CrossAxisAlignment.END,
                scroll=ScrollMode.AUTO,
            ),
            height=bar_max_height + 70,
        )
        
        return Card(
            content=Container(
                content=Column([
                    Text(title, size=14, weight=FontWeight.BOLD, color=ATBU_DARK),
                    chart,
                ]),
                padding=Padding.all(16),
            ),
            elevation=2,
        )
    
    def _build_pie_chart(self, title, data):
        """Build a pie chart representation using legend with percentages."""
        if not data:
            return Container(
                content=Text("No data available", italic=True, color=ATBU_MUTED),
                padding=Padding.all(16),
            )
        
        color_list = [
            ATBU_GREEN, "#2196F3", ATBU_GOLD, "#9C27B0", "#00BCD4",
            "#FF5722", "#607D8B", "#E91E63",
        ]
        total = sum(v for _, v in data)
        
        legend_items = []
        bar_segments = []
        for i, (label, value) in enumerate(data):
            pct = (value / total * 100) if total > 0 else 0
            color = color_list[i % len(color_list)]
            bar_segments.append(
                Container(
                    height=24,
                    expand=value,
                    bgcolor=color,
                    content=Text(f"{pct:.0f}%" if pct > 10 else "",
                                size=9, color=Colors.WHITE,
                                weight=FontWeight.BOLD),
                    alignment=Alignment.CENTER,
                )
            )
            legend_items.append(
                Row([
                    Container(width=14, height=14, bgcolor=color,
                             border_radius=3),
                    Text(f"{label}: {value} ({pct:.0f}%)", size=11,
                         color=ATBU_DARK, weight=FontWeight.BOLD if i == 0 else FontWeight.NORMAL),
                ], spacing=8)
            )
        
        # Horizontal stacked bar as pie alternative
        total_bar = Container(
            content=Row(bar_segments, spacing=0),
            border_radius=BorderRadius.all(12),
            # clip_content was removed (not supported in Flet 0.86.3)
        )
        
        return Card(
            content=Container(
                content=Column([
                    Text(title, size=14, weight=FontWeight.BOLD, color=ATBU_DARK),
                    Container(height=8),
                    total_bar,
                    Container(height=12),
                    Column(legend_items, spacing=6),
                ]),
                padding=Padding.all(16),
            ),
            elevation=2,
        )
