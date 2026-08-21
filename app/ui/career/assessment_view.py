from __future__ import annotations
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFrame, QMessageBox
)
from app.core.config import COLORS
from app.career.career_data import get_career_by_id, load_career_database
from app.career.matcher import CareerMatcher, CareerMatchResult
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository
from app.ui.career.results_view import ResultsView
from app.ui.career.career_detail_view import CareerDetailDialog

class AssessmentView(QWidget):
    request_roadmap = Signal(str)  # career_id
    request_resume = Signal(str)   # career_id
    request_learning = Signal(str) # skill or career_id

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.all_results: List[CareerMatchResult] = []
        self.current_profile: Optional[StudentProfile] = None
        self.init_ui()
        self.run_analysis()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        # Control Bar Card
        control_card = QFrame()
        control_card.setProperty("class", "card")
        c_layout = QVBoxLayout(control_card)
        c_layout.setSpacing(12)

        top_row = QHBoxLayout()
        info_box = QVBoxLayout()
        title_lbl = QLabel("Career Recommendation & Alignment Engine")
        title_lbl.setProperty("class", "card-title")
        sub_lbl = QLabel("Deterministic offline ranking weighted by: Skills (50%), Interests (35%), and Academic Background (15%).")
        sub_lbl.setProperty("class", "card-subtitle")
        info_box.addWidget(title_lbl)
        info_box.addWidget(sub_lbl)
        top_row.addLayout(info_box)

        self.analyze_btn = QPushButton("⚡ Re-Analyze My Career")
        self.analyze_btn.setProperty("class", "btn-primary")
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.clicked.connect(self.run_analysis)
        top_row.addWidget(self.analyze_btn)
        c_layout.addLayout(top_row)

        # Filter & Search Row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search careers by keyword, framework, or skill...")
        self.search_edit.textChanged.connect(self._apply_filters)
        filter_row.addWidget(self.search_edit, stretch=2)

        self.cat_combo = QComboBox()
        self.cat_combo.addItems([
            "All Categories", "Artificial Intelligence & ML", "Software Engineering",
            "Web & Cloud Services", "Web & UI Engineering", "Data Science & Analytics",
            "Security & Infrastructure", "Cloud & Infrastructure", "DevOps & SRE", "Mobile App Engineering"
        ])
        self.cat_combo.currentIndexChanged.connect(self._apply_filters)
        filter_row.addWidget(self.cat_combo, stretch=1)

        c_layout.addLayout(filter_row)
        layout.addWidget(control_card)

        # Results Grid View
        self.results_view = ResultsView()
        self.results_view.open_career_detail.connect(self.show_career_deep_dive)
        self.results_view.open_career_roadmap.connect(self.request_roadmap.emit)
        layout.addWidget(self.results_view, stretch=1)

    def run_analysis(self) -> None:
        self.current_profile = ProfileRepository.get_profile()
        if not self.current_profile or not self.current_profile.skills:
            # Create a graceful default profile if empty
            self.current_profile = StudentProfile(
                name="Student",
                email="student@university.edu",
                skills=["Python", "SQL", "Git", "React"],
                interests=["Software Engineering", "Artificial Intelligence"]
            )

        self.all_results = CareerMatcher.rank_careers(self.current_profile)
        self._apply_filters()

    def _apply_filters(self) -> None:
        query = self.search_edit.text().strip().lower()
        selected_cat = self.cat_combo.currentText()

        filtered: List[CareerMatchResult] = []
        for r in self.all_results:
            if selected_cat != "All Categories" and r.category != selected_cat:
                continue
            if query:
                corpus = f"{r.career_name} {r.category} {r.description} {' '.join(r.career.required_skills)}".lower()
                if query not in corpus:
                    continue
            filtered.append(r)

        self.results_view.display_results(filtered)

    def show_career_deep_dive(self, career_id: str) -> None:
        career = get_career_by_id(career_id)
        if not career:
            return
        if not self.current_profile:
            self.current_profile = ProfileRepository.get_profile() or StudentProfile()

        dialog = CareerDetailDialog(career, self.current_profile, self)
        dialog.navigate_to_roadmap.connect(self.request_roadmap.emit)
        dialog.navigate_to_resume.connect(self.request_resume.emit)
        dialog.navigate_to_learning.connect(self.request_learning.emit)
        dialog.exec()
