from __future__ import annotations
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QProgressBar
)
from app.core.config import COLORS
from app.career.matcher import CareerMatchResult
from app.database.models import StudentProfile
from app.ui.career.career_detail_view import CareerDetailDialog

class CareerCard(QFrame):
    view_detail_requested = Signal(str)      # career_id
    generate_roadmap_requested = Signal(str) # career_id

    def __init__(self, match_result: CareerMatchResult, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.match_result = match_result
        self.setProperty("class", "card")
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Top row: Title + Category + Score Badge
        top_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        name_lbl = QLabel(self.match_result.career_name)
        name_lbl.setStyleSheet(f"font-size: 17px; font-weight: 800; color: {COLORS.TEXT_MAIN};")
        title_box.addWidget(name_lbl)

        cat_lbl = QLabel(self.match_result.category)
        cat_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_MUTED}; font-weight: 600;")
        title_box.addWidget(cat_lbl)
        top_row.addLayout(title_box)

        top_row.addStretch()

        # Score Badge
        score_val = self.match_result.score
        if score_val >= 75:
            badge_bg = COLORS.SUCCESS_BG
            badge_border = COLORS.SUCCESS
            badge_color = COLORS.SUCCESS
        elif score_val >= 45:
            badge_bg = COLORS.PRIMARY_MUTED
            badge_border = COLORS.PRIMARY
            badge_color = COLORS.PRIMARY_LIGHT
        else:
            badge_bg = COLORS.WARNING_BG
            badge_border = COLORS.WARNING
            badge_color = COLORS.WARNING

        score_badge = QLabel(f" {score_val}% Profile Match ")
        score_badge.setStyleSheet(f"""
            background-color: {badge_bg};
            border: 1px solid {badge_border};
            color: {badge_color};
            border-radius: 12px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 800;
        """)
        top_row.addWidget(score_badge)

        layout.addLayout(top_row)

        # Description
        desc_lbl = QLabel(self.match_result.description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"color: {COLORS.TEXT_MUTED}; font-size: 12px; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        # Progress / Match bar
        bar_row = QVBoxLayout()
        bar_row.setSpacing(4)
        bar_lbl = QLabel(f"Skill Alignment: {len(self.match_result.matched_skills)}/{len(self.match_result.career.required_skills)} required skills matched")
        bar_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_SUBTLE};")
        bar = QProgressBar()
        bar.setValue(int(self.match_result.skill_score))
        bar_row.addWidget(bar_lbl)
        bar_row.addWidget(bar)
        layout.addLayout(bar_row)

        # Matched / Missing preview tags
        tags_row = QHBoxLayout()
        tags_row.setSpacing(6)
        
        if self.match_result.matched_skills:
            for s in self.match_result.matched_skills[:3]:
                tag = QLabel(f"✔ {s}")
                tag.setStyleSheet(f"""
                    background-color: {COLORS.SUCCESS_BG};
                    color: {COLORS.SUCCESS};
                    border-radius: 8px;
                    padding: 2px 6px;
                    font-size: 10px;
                    font-weight: 600;
                """)
                tags_row.addWidget(tag)

        if self.match_result.missing_skills:
            for s in self.match_result.missing_skills[:2]:
                tag = QLabel(f"⚠ {s}")
                tag.setStyleSheet(f"""
                    background-color: {COLORS.WARNING_BG};
                    color: {COLORS.WARNING};
                    border-radius: 8px;
                    padding: 2px 6px;
                    font-size: 10px;
                    font-weight: 600;
                """)
                tags_row.addWidget(tag)

        tags_row.addStretch()
        layout.addLayout(tags_row)

        # Card Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        detail_btn = QPushButton("Deep Dive & Skill Gap")
        detail_btn.setProperty("class", "btn-secondary")
        detail_btn.setCursor(Qt.PointingHandCursor)
        detail_btn.clicked.connect(lambda: self.view_detail_requested.emit(self.match_result.career_id))
        btn_row.addWidget(detail_btn)

        roadmap_btn = QPushButton("Explore Roadmap")
        roadmap_btn.setProperty("class", "btn-primary")
        roadmap_btn.setCursor(Qt.PointingHandCursor)
        roadmap_btn.clicked.connect(lambda: self.generate_roadmap_requested.emit(self.match_result.career_id))
        btn_row.addWidget(roadmap_btn)

        layout.addLayout(btn_row)

class ResultsView(QWidget):
    open_career_detail = Signal(str)      # career_id
    open_career_roadmap = Signal(str)     # career_id

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.results: List[CareerMatchResult] = []
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.container_widget = QWidget()
        self.grid_layout = QGridLayout(self.container_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(16)

        self.scroll_area.setWidget(self.container_widget)
        layout.addWidget(self.scroll_area)

    def display_results(self, match_results: List[CareerMatchResult]) -> None:
        self.results = match_results
        # Clear existing
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not match_results:
            empty_lbl = QLabel("No career paths found matching your criteria.")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet(f"color: {COLORS.TEXT_MUTED}; font-size: 14px; padding: 40px;")
            self.grid_layout.addWidget(empty_lbl, 0, 0)
            return

        cols = 2
        for idx, res in enumerate(match_results):
            card = CareerCard(res)
            card.view_detail_requested.connect(self.open_career_detail.emit)
            card.generate_roadmap_requested.connect(self.open_career_roadmap.emit)
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col)
