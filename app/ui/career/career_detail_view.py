from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QProgressBar
)
from app.core.config import COLORS
from app.career.career_data import Career
from app.career.skill_gap import SkillGapAnalyzer, SkillGapAnalysis
from app.database.models import StudentProfile

class CareerDetailDialog(QDialog):
    navigate_to_roadmap = Signal(str)  # career_id
    navigate_to_resume = Signal(str)   # career_id
    navigate_to_learning = Signal(str) # skill or career_id

    def __init__(self, career: Career, profile: StudentProfile, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.career = career
        self.profile = profile
        self.gap_analysis = SkillGapAnalyzer.analyze(profile, career)
        self.setWindowTitle(f"Career Deep Dive: {career.name}")
        self.setMinimumSize(780, 640)
        self.setStyleSheet(f"background-color: {COLORS.BG_DARK};")
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        # Header Card
        header_card = QFrame()
        header_card.setProperty("class", "card-highlight")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(8)

        top_row = QHBoxLayout()
        title_lbl = QLabel(self.career.name)
        title_lbl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {COLORS.PRIMARY_LIGHT};")
        top_row.addWidget(title_lbl)

        cat_badge = QLabel(f" {self.career.category} ")
        cat_badge.setStyleSheet(f"""
            background-color: {COLORS.PRIMARY_MUTED};
            border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 700;
            color: {COLORS.PRIMARY_LIGHT};
        """)
        top_row.addWidget(cat_badge)
        top_row.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setStyleSheet(f"background: transparent; color: {COLORS.TEXT_MUTED}; font-size: 16px; font-weight: bold; border: none;")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        top_row.addWidget(close_btn)
        h_layout.addLayout(top_row)

        desc_lbl = QLabel(self.career.description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"color: {COLORS.TEXT_MAIN}; font-size: 13px; line-height: 1.4;")
        h_layout.addWidget(desc_lbl)

        # Meta tags row
        meta_row = QHBoxLayout()
        meta_row.setSpacing(16)
        sal_lbl = QLabel(f"💰 Average Compensation: <b>{self.career.salary_range}</b>")
        sal_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS.TEXT_MUTED};")
        dem_lbl = QLabel(f"📈 Industry Demand: <b>{self.career.market_demand}</b>")
        dem_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS.TEXT_MUTED};")
        meta_row.addWidget(sal_lbl)
        meta_row.addWidget(dem_lbl)
        meta_row.addStretch()
        h_layout.addLayout(meta_row)

        layout.addWidget(header_card)

        # Scrollable Analysis Details
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        scroll_widget = QWidget()
        s_layout = QVBoxLayout(scroll_widget)
        s_layout.setContentsMargins(0, 0, 0, 0)
        s_layout.setSpacing(16)

        # Readiness Metrics Card
        metrics_card = QFrame()
        metrics_card.setProperty("class", "card")
        m_layout = QVBoxLayout(metrics_card)
        m_layout.setSpacing(12)

        m_title = QLabel("Deterministic Readiness Assessment")
        m_title.setProperty("class", "card-title")
        m_layout.addWidget(m_title)

        m_grid = QGridLayout()
        m_grid.setHorizontalSpacing(20)
        m_grid.setVerticalSpacing(10)

        # Skill Readiness
        sk_lbl = QLabel(f"Skill Readiness: <b>{self.gap_analysis.skill_readiness}%</b> ({len(self.gap_analysis.matched_skills)}/{len(self.career.required_skills)} core skills)")
        sk_lbl.setStyleSheet(f"font-size: 13px; color: {COLORS.TEXT_MAIN};")
        sk_bar = QProgressBar()
        sk_bar.setValue(int(self.gap_analysis.skill_readiness))
        m_grid.addWidget(sk_lbl, 0, 0)
        m_grid.addWidget(sk_bar, 1, 0)

        # Overall Readiness
        ov_lbl = QLabel(f"Overall Profile Readiness: <b>{self.gap_analysis.overall_readiness}%</b> ({self.gap_analysis.readiness_level})")
        ov_lbl.setStyleSheet(f"font-size: 13px; color: {COLORS.TEXT_MAIN};")
        ov_bar = QProgressBar()
        ov_bar.setValue(int(self.gap_analysis.overall_readiness))
        m_grid.addWidget(ov_lbl, 0, 1)
        m_grid.addWidget(ov_bar, 1, 1)

        m_layout.addLayout(m_grid)
        s_layout.addWidget(metrics_card)

        # Skill Breakdown Card
        skills_card = QFrame()
        skills_card.setProperty("class", "card")
        sk_layout = QVBoxLayout(skills_card)
        sk_layout.setSpacing(12)

        sk_sec_title = QLabel("Skill Alignment & Missing Gap Breakdown")
        sk_sec_title.setProperty("class", "card-title")
        sk_layout.addWidget(sk_sec_title)

        # Matched Skills
        matched_box = QVBoxLayout()
        matched_hdr = QLabel(f"✔ Matched Skills ({len(self.gap_analysis.matched_skills)}):")
        matched_hdr.setStyleSheet(f"color: {COLORS.SUCCESS}; font-weight: 700; font-size: 13px;")
        matched_box.addWidget(matched_hdr)

        matched_chips = QHBoxLayout()
        matched_chips.setSpacing(8)
        if self.gap_analysis.matched_skills:
            for s in self.gap_analysis.matched_skills:
                chip = QLabel(f" {s} ")
                chip.setStyleSheet(f"""
                    background-color: {COLORS.SUCCESS_BG};
                    border: 1px solid {COLORS.SUCCESS};
                    color: {COLORS.SUCCESS};
                    border-radius: 10px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: 600;
                """)
                matched_chips.addWidget(chip)
        else:
            none_lbl = QLabel("No direct core skills matched yet.")
            none_lbl.setStyleSheet(f"color: {COLORS.TEXT_SUBTLE}; font-style: italic;")
            matched_chips.addWidget(none_lbl)
        matched_chips.addStretch()
        matched_box.addLayout(matched_chips)
        sk_layout.addLayout(matched_box)

        # Missing Skills
        missing_box = QVBoxLayout()
        missing_hdr = QLabel(f"⚠ Missing Required Skills ({len(self.gap_analysis.missing_skills)}):")
        missing_hdr.setStyleSheet(f"color: {COLORS.WARNING}; font-weight: 700; font-size: 13px; margin-top: 8px;")
        missing_box.addWidget(missing_hdr)

        missing_chips = QHBoxLayout()
        missing_chips.setSpacing(8)
        if self.gap_analysis.missing_skills:
            for s in self.gap_analysis.missing_skills:
                chip = QLabel(f" {s} ")
                chip.setStyleSheet(f"""
                    background-color: {COLORS.WARNING_BG};
                    border: 1px solid {COLORS.WARNING};
                    color: {COLORS.WARNING};
                    border-radius: 10px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: 600;
                """)
                missing_chips.addWidget(chip)
        else:
            all_lbl = QLabel("All core required skills matched! Ready for advanced capstones.")
            all_lbl.setStyleSheet(f"color: {COLORS.SUCCESS}; font-weight: 600;")
            missing_chips.addWidget(all_lbl)
        missing_chips.addStretch()
        missing_box.addLayout(missing_chips)
        sk_layout.addLayout(missing_box)

        s_layout.addWidget(skills_card)

        # Responsibilities & Next Steps Card
        steps_card = QFrame()
        steps_card.setProperty("class", "card")
        st_layout = QVBoxLayout(steps_card)
        st_layout.setSpacing(10)

        st_title = QLabel("Recommended Action Steps to Bridge the Gap")
        st_title.setProperty("class", "card-title")
        st_layout.addWidget(st_title)

        for step in self.gap_analysis.actionable_steps:
            item_lbl = QLabel(f"• {step}")
            item_lbl.setWordWrap(True)
            item_lbl.setStyleSheet(f"font-size: 13px; color: {COLORS.TEXT_MAIN}; line-height: 1.4;")
            st_layout.addWidget(item_lbl)

        s_layout.addWidget(steps_card)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Bottom Action Bar
        action_bar = QHBoxLayout()
        action_bar.setSpacing(12)

        learn_btn = QPushButton("📚 View Learning Resources")
        learn_btn.setProperty("class", "btn-secondary")
        learn_btn.setCursor(Qt.PointingHandCursor)
        learn_btn.clicked.connect(self._on_learning_clicked)
        action_bar.addWidget(learn_btn)

        resume_btn = QPushButton("📄 Build Tailored Resume")
        resume_btn.setProperty("class", "btn-secondary")
        resume_btn.setCursor(Qt.PointingHandCursor)
        resume_btn.clicked.connect(self._on_resume_clicked)
        action_bar.addWidget(resume_btn)

        action_bar.addStretch()

        roadmap_btn = QPushButton("🗺️ Generate Roadmap for this Career")
        roadmap_btn.setProperty("class", "btn-primary")
        roadmap_btn.setCursor(Qt.PointingHandCursor)
        roadmap_btn.clicked.connect(self._on_roadmap_clicked)
        action_bar.addWidget(roadmap_btn)

        layout.addLayout(action_bar)

    def _on_roadmap_clicked(self) -> None:
        self.accept()
        self.navigate_to_roadmap.emit(self.career.id)

    def _on_resume_clicked(self) -> None:
        self.accept()
        self.navigate_to_resume.emit(self.career.id)

    def _on_learning_clicked(self) -> None:
        self.accept()
        self.navigate_to_learning.emit(self.career.id)
