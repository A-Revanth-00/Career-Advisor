from __future__ import annotations
from typing import List, Optional
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFrame, QScrollArea, QGridLayout, QMessageBox
)
from app.core.config import COLORS
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository
from app.career.career_data import get_career_by_id, get_career_by_name
from app.career.skill_gap import SkillGapAnalyzer
from app.learning.resource_database import (
    LearningResource, load_learning_resources, filter_resources, get_all_skills_in_resources
)

class ResourceCard(QFrame):
    def __init__(self, resource: LearningResource, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.resource = resource
        self.setProperty("class", "card")
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Header: Title + Provider
        top_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        t_lbl = QLabel(self.resource.title)
        t_lbl.setWordWrap(True)
        t_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLORS.TEXT_MAIN};")
        title_box.addWidget(t_lbl)

        p_lbl = QLabel(f"by {self.resource.provider}")
        p_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_MUTED};")
        title_box.addWidget(p_lbl)
        top_row.addLayout(title_box)

        layout.addLayout(top_row)

        # Description
        desc_lbl = QLabel(self.resource.description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS.TEXT_MUTED}; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        # Badges row
        badges_row = QHBoxLayout()
        badges_row.setSpacing(6)

        # Skill badge
        sk_badge = QLabel(f" {self.resource.skill} ")
        sk_badge.setStyleSheet(f"""
            background-color: {COLORS.PRIMARY_MUTED};
            color: {COLORS.PRIMARY_LIGHT};
            border-radius: 6px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 600;
        """)
        badges_row.addWidget(sk_badge)

        # Type badge
        type_badge = QLabel(f" {self.resource.type} ")
        type_badge.setStyleSheet(f"""
            background-color: {COLORS.BG_INPUT};
            border: 1px solid {COLORS.BORDER};
            color: {COLORS.TEXT_MAIN};
            border-radius: 6px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 600;
        """)
        badges_row.addWidget(type_badge)

        # Difficulty badge
        diff_color = COLORS.SUCCESS if self.resource.difficulty == "Beginner" else COLORS.WARNING if self.resource.difficulty == "Intermediate" else COLORS.DANGER
        diff_badge = QLabel(f" {self.resource.difficulty} ")
        diff_badge.setStyleSheet(f"""
            background-color: {COLORS.BG_INPUT};
            border: 1px solid {diff_color};
            color: {diff_color};
            border-radius: 6px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 600;
        """)
        badges_row.addWidget(diff_badge)

        badges_row.addStretch()

        hrs_lbl = QLabel(f"⏱ {self.resource.estimated_hours}h")
        hrs_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {COLORS.TEXT_MUTED};")
        badges_row.addWidget(hrs_lbl)

        layout.addLayout(badges_row)

        # Action Link Buttons Row
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        link_btn = QPushButton("🌐 Open Resource")
        link_btn.setProperty("class", "btn-secondary")
        link_btn.setCursor(Qt.PointingHandCursor)
        link_btn.clicked.connect(self.open_url)
        actions_row.addWidget(link_btn)

        if self.resource.youtube_url:
            yt_btn = QPushButton("▶ Watch Video")
            yt_btn.setCursor(Qt.PointingHandCursor)
            yt_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ef4444;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 11px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background-color: #dc2626;
                }}
            """)
            yt_btn.clicked.connect(self.open_youtube)
            actions_row.addWidget(yt_btn)

        layout.addLayout(actions_row)

    def open_url(self) -> None:
        if self.resource.url:
            QDesktopServices.openUrl(QUrl(self.resource.url))

    def open_youtube(self) -> None:
        if self.resource.youtube_url:
            QDesktopServices.openUrl(QUrl(self.resource.youtube_url))

class LearningView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_profile: Optional[StudentProfile] = None
        self.init_ui()
        self.reload_resources()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(14)

        # Header & Filter Card
        header_card = QFrame()
        header_card.setProperty("class", "card")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(12)

        top_box = QVBoxLayout()
        t_lbl = QLabel("Offline Learning Resource Hub")
        t_lbl.setProperty("class", "card-title")
        sub_lbl = QLabel("Curated courses, documentation, and exercises mapped to industry skills and career paths.")
        sub_lbl.setProperty("class", "card-subtitle")
        top_box.addWidget(t_lbl)
        top_box.addWidget(sub_lbl)
        h_layout.addLayout(top_box)

        # Filter Bar
        f_row = QHBoxLayout()
        f_row.setSpacing(10)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search resources by title, provider, or topic...")
        self.search_edit.textChanged.connect(self._apply_filters)
        f_row.addWidget(self.search_edit, stretch=2)

        self.skill_combo = QComboBox()
        self.skill_combo.addItem("All Skills")
        for s in get_all_skills_in_resources():
            self.skill_combo.addItem(s)
        self.skill_combo.currentIndexChanged.connect(self._apply_filters)
        f_row.addWidget(self.skill_combo, stretch=1)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Types", "Documentation", "Course", "Practice", "Video", "Project"])
        self.type_combo.currentIndexChanged.connect(self._apply_filters)
        f_row.addWidget(self.type_combo, stretch=1)

        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["All Difficulties", "Beginner", "Intermediate", "Advanced"])
        self.diff_combo.currentIndexChanged.connect(self._apply_filters)
        f_row.addWidget(self.diff_combo, stretch=1)

        h_layout.addLayout(f_row)
        main_layout.addWidget(header_card)

        # Scrollable Grid of Resources
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(14)

        scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(scroll_area, stretch=1)

    def reload_resources(self) -> None:
        self.current_profile = ProfileRepository.get_profile() or StudentProfile()
        self._apply_filters()

    def filter_by_skill_tag(self, skill: str) -> None:
        idx = self.skill_combo.findText(skill, Qt.MatchContains)
        if idx >= 0:
            self.skill_combo.setCurrentIndex(idx)
        else:
            self.search_edit.setText(skill)

    def _apply_filters(self) -> None:
        query = self.search_edit.text().strip()
        sk_filter = self.skill_combo.currentText()
        if sk_filter == "All Skills":
            sk_filter = None
        t_filter = self.type_combo.currentText()
        if t_filter == "All Types":
            t_filter = None
        d_filter = self.diff_combo.currentText()
        if d_filter == "All Difficulties":
            d_filter = None

        results = filter_resources(
            skill_filter=sk_filter,
            type_filter=t_filter,
            difficulty_filter=d_filter,
            search_query=query
        )

        # Clear existing
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not results:
            empty_lbl = QLabel("No learning resources match your current filter.")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet(f"color: {COLORS.TEXT_MUTED}; font-size: 14px; padding: 40px;")
            self.grid_layout.addWidget(empty_lbl, 0, 0)
            return

        cols = 2
        for idx, r in enumerate(results):
            card = ResourceCard(r)
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col)
