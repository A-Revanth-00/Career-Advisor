from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QProgressBar
)
from app.core.config import COLORS
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository, ResumeRepository
from app.career.career_data import get_career_by_id, get_career_by_name, load_career_database
from app.career.matcher import CareerMatcher
from app.career.skill_gap import SkillGapAnalyzer
from app.roadmap.roadmap_generator import RoadmapGenerator
from app.roadmap.progress import RoadmapProgressTracker
from app.resume.resume_builder import ResumeBuilder
from app.resume.ats_analyzer import LocalATSAnalyzer

class MetricCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str, color: str = COLORS.PRIMARY_LIGHT, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("class", "card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "metric-label")
        layout.addWidget(lbl_title)

        self.lbl_val = QLabel(value)
        self.lbl_val.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {color};")
        layout.addWidget(self.lbl_val)

        self.lbl_sub = QLabel(subtitle)
        self.lbl_sub.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_MUTED};")
        layout.addWidget(self.lbl_sub)

    def update_metrics(self, value: str, subtitle: str) -> None:
        self.lbl_val.setText(value)
        self.lbl_sub.setText(subtitle)

class DashboardView(QWidget):
    navigate_to_profile = Signal()
    navigate_to_career = Signal()
    navigate_to_roadmap = Signal(str)  # career_id
    navigate_to_resume = Signal(str)   # career_id
    navigate_to_learning = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_profile: Optional[StudentProfile] = None
        self.init_ui()
        self.refresh_dashboard()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(16)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # 1. Welcome & Getting Started Banner
        self.banner_card = QFrame()
        self.banner_card.setProperty("class", "card-highlight")
        b_layout = QHBoxLayout(self.banner_card)
        b_layout.setContentsMargins(20, 16, 20, 16)
        b_layout.setSpacing(16)

        b_text_box = QVBoxLayout()
        self.banner_title = QLabel("Welcome to Career Advisor")
        self.banner_title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {COLORS.PRIMARY_LIGHT};")
        self.banner_sub = QLabel("Complete your student profile to unlock deterministic career recommendations and weekly roadmap scheduling.")
        self.banner_sub.setStyleSheet(f"font-size: 12px; color: {COLORS.TEXT_MAIN};")
        b_text_box.addWidget(self.banner_title)
        b_text_box.addWidget(self.banner_sub)
        b_layout.addLayout(b_text_box, stretch=1)

        self.banner_action_btn = QPushButton("Complete Profile")
        self.banner_action_btn.setProperty("class", "btn-primary")
        self.banner_action_btn.setCursor(Qt.PointingHandCursor)
        self.banner_action_btn.clicked.connect(self._on_banner_action)
        b_layout.addWidget(self.banner_action_btn)

        layout.addWidget(self.banner_card)

        # 2. Key Metrics Grid
        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(16)
        metrics_grid.setVerticalSpacing(16)

        self.card_match = MetricCard("Career Match", "0.0%", "Based on profile skills", COLORS.PRIMARY_LIGHT)
        self.card_readiness = MetricCard("Career Readiness", "0.0%", "Skill gap alignment", COLORS.ACCENT_LIGHT)
        self.card_roadmap = MetricCard("Roadmap Progress", "0.0%", "0 of 0 tasks completed", COLORS.SUCCESS)
        self.card_ats = MetricCard("Resume ATS Score", "0 / 100", "Heuristic format rating", COLORS.WARNING)

        metrics_grid.addWidget(self.card_match, 0, 0)
        metrics_grid.addWidget(self.card_readiness, 0, 1)
        metrics_grid.addWidget(self.card_roadmap, 0, 2)
        metrics_grid.addWidget(self.card_ats, 0, 3)

        layout.addLayout(metrics_grid)

        # 3. Two-Column Dashboard Content
        content_row = QHBoxLayout()
        content_row.setSpacing(16)

        # Left Column: Top Recommended Careers
        left_box = QVBoxLayout()
        left_box.setSpacing(12)

        rec_header = QHBoxLayout()
        rec_title = QLabel("🎯 Top Career Matches")
        rec_title.setProperty("class", "card-title")
        rec_header.addWidget(rec_title)
        rec_header.addStretch()

        view_all_careers_btn = QPushButton("View Career Guide →")
        view_all_careers_btn.setProperty("class", "btn-secondary")
        view_all_careers_btn.setCursor(Qt.PointingHandCursor)
        view_all_careers_btn.clicked.connect(self.navigate_to_career.emit)
        rec_header.addWidget(view_all_careers_btn)
        left_box.addLayout(rec_header)

        self.careers_container = QVBoxLayout()
        self.careers_container.setSpacing(10)
        left_box.addLayout(self.careers_container)
        content_row.addLayout(left_box, stretch=1)

        # Right Column: Active Roadmap Milestone & Actions
        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        road_header = QHBoxLayout()
        road_title = QLabel("🗺️ Active Roadmap Next Tasks")
        road_title.setProperty("class", "card-title")
        road_header.addWidget(road_title)
        road_header.addStretch()

        view_full_road_btn = QPushButton("Full Roadmap →")
        view_full_road_btn.setProperty("class", "btn-secondary")
        view_full_road_btn.setCursor(Qt.PointingHandCursor)
        view_full_road_btn.clicked.connect(lambda: self.navigate_to_roadmap.emit(self.current_profile.career_goal if self.current_profile else ""))
        road_header.addWidget(view_full_road_btn)
        right_box.addLayout(road_header)

        self.tasks_container = QVBoxLayout()
        self.tasks_container.setSpacing(10)
        right_box.addLayout(self.tasks_container)

        content_row.addLayout(right_box, stretch=1)
        layout.addLayout(content_row)

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

    def _on_banner_action(self) -> None:
        if not self.current_profile or not self.current_profile.is_complete:
            self.navigate_to_profile.emit()
        else:
            self.navigate_to_career.emit()

    def refresh_dashboard(self) -> None:
        self.current_profile = ProfileRepository.get_profile() or StudentProfile()
        
        # 1. Update Banner
        if not self.current_profile.name.strip() or not self.current_profile.skills:
            self.banner_title.setText("👋 Welcome! Set Up Your Profile")
            self.banner_sub.setText("Enter your degree, skills, and weekly study availability to unlock offline recommendations.")
            self.banner_action_btn.setText("Edit Profile")
        else:
            self.banner_title.setText(f"🎯 Welcome back, {self.current_profile.name}!")
            self.banner_sub.setText(f"Targeting <b>{self.current_profile.career_goal}</b> &bull; Available <b>{self.current_profile.weekly_hours} hrs/week</b> for skill progression.")
            self.banner_action_btn.setText("Explore Career Guide")

        # 2. Match Scores & Readiness
        careers = load_career_database()
        if careers and self.current_profile.skills:
            ranked = CareerMatcher.rank_careers(self.current_profile)
            top_match = ranked[0]
            self.card_match.update_metrics(f"{top_match.score}%", f"Top: {top_match.career_name}")

            # Career target readiness
            target_career = get_career_by_id(self.current_profile.career_goal) or get_career_by_name(self.current_profile.career_goal) or top_match.career
            gap = SkillGapAnalyzer.analyze(self.current_profile, target_career)
            self.card_readiness.update_metrics(f"{gap.overall_readiness}%", f"{target_career.name} ({gap.readiness_level})")

            # Roadmap Progress
            roadmap = RoadmapGenerator.generate(self.current_profile, target_career)
            progress = RoadmapProgressTracker.get_progress(roadmap)
            self.card_roadmap.update_metrics(
                f"{progress.percentage}%",
                f"{progress.completed_tasks_count}/{progress.total_tasks} tasks ({progress.completed_hours}h completed)"
            )

            # Resume ATS
            saved_resume_data = ResumeRepository.get_resume(target_career.name)
            if saved_resume_data:
                res_obj = ResumeBuilder.build_from_profile(self.current_profile, target_career.id)
            else:
                res_obj = ResumeBuilder.build_from_profile(self.current_profile, target_career.id)
            ats = LocalATSAnalyzer.analyze(res_obj)
            self.card_ats.update_metrics(f"{ats.score} / 100", f"Grade: {ats.grade} for {target_career.name}")

            # Render Top 3 Careers
            self._render_top_careers(ranked[:3])

            # Render Next Roadmap Tasks
            self._render_roadmap_tasks(roadmap, progress)
        else:
            self.card_match.update_metrics("0.0%", "Add skills to calculate")
            self.card_readiness.update_metrics("0.0%", "Profile required")
            self.card_roadmap.update_metrics("0.0%", "0 tasks")
            self.card_ats.update_metrics("0 / 100", "Generate resume")

    def _render_top_careers(self, top_list) -> None:
        while self.careers_container.count():
            item = self.careers_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for res in top_list:
            c_card = QFrame()
            c_card.setProperty("class", "card")
            c_lay = QVBoxLayout(c_card)
            c_lay.setContentsMargins(12, 10, 12, 10)
            c_lay.setSpacing(6)

            r1 = QHBoxLayout()
            name_lbl = QLabel(f"<b>{res.career_name}</b>")
            name_lbl.setStyleSheet(f"font-size: 14px; color: {COLORS.TEXT_MAIN};")
            r1.addWidget(name_lbl)
            r1.addStretch()

            badge = QLabel(f" {res.score}% Match ")
            badge.setStyleSheet(f"""
                background-color: {COLORS.PRIMARY_MUTED};
                color: {COLORS.PRIMARY_LIGHT};
                border-radius: 6px;
                padding: 2px 6px;
                font-weight: 700;
                font-size: 11px;
            """)
            r1.addWidget(badge)
            c_lay.addLayout(r1)

            sk_text = f"<span style='color: {COLORS.SUCCESS};'>✔ {', '.join(res.matched_skills[:3])}</span>" if res.matched_skills else "<span style='color: {COLORS.TEXT_SUBTLE};'>No core skills matched yet</span>"
            sk_lbl = QLabel(sk_text)
            sk_lbl.setStyleSheet("font-size: 11px;")
            c_lay.addWidget(sk_lbl)

            btn_row = QHBoxLayout()
            road_btn = QPushButton("Open Roadmap")
            road_btn.setProperty("class", "btn-secondary")
            road_btn.setCursor(Qt.PointingHandCursor)
            road_btn.clicked.connect(lambda checked=False, cid=res.career_id: self.navigate_to_roadmap.emit(cid))
            btn_row.addWidget(road_btn)
            c_lay.addLayout(btn_row)

            self.careers_container.addWidget(c_card)

    def _render_roadmap_tasks(self, roadmap, progress) -> None:
        while self.tasks_container.count():
            item = self.tasks_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        uncompleted = [t for t in roadmap.tasks if t.id not in progress.completed_task_ids]
        show_tasks = uncompleted[:4] if uncompleted else roadmap.tasks[:4]

        for t in show_tasks:
            t_card = QFrame()
            t_card.setProperty("class", "card")
            t_lay = QVBoxLayout(t_card)
            t_lay.setContentsMargins(12, 10, 12, 10)
            t_lay.setSpacing(4)

            h_line = QHBoxLayout()
            is_comp = t.id in progress.completed_task_ids
            status_symbol = "✔" if is_comp else "⏱"
            status_color = COLORS.SUCCESS if is_comp else COLORS.WARNING
            lbl = QLabel(f"<span style='color:{status_color}; font-weight:bold;'>{status_symbol}</span> <b>{t.title}</b>")
            lbl.setStyleSheet(f"font-size: 13px; color: {COLORS.TEXT_MAIN};")
            h_line.addWidget(lbl, stretch=1)

            hrs_lbl = QLabel(f"{t.estimated_hours}h")
            hrs_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLORS.TEXT_MUTED};")
            h_line.addWidget(hrs_lbl)
            t_lay.addLayout(h_line)

            sub = QLabel(f"{t.phase_title} &bull; {t.skill}")
            sub.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_SUBTLE};")
            t_lay.addWidget(sub)

            self.tasks_container.addWidget(t_card)
