from __future__ import annotations
from typing import List, Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QButtonGroup, QMessageBox
)
from app.core.config import APP_NAME, APP_TAGLINE, COLORS
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository
from app.ui.theme import APP_STYLESHEET
from app.ui.dashboard.dashboard_view import DashboardView
from app.ui.profile.profile import ProfileView
from app.ui.career.assessment_view import AssessmentView
from app.ui.roadmap.roadmap_view import RoadmapView
from app.ui.resume.resume_view import ResumeView
from app.ui.learning.learning_view import LearningView
from app.ui.settings.settings_view import SettingsView

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - {APP_TAGLINE}")
        self.resize(1280, 820)
        self.setMinimumSize(1050, 680)
        self.setStyleSheet(APP_STYLESHEET)

        self.current_profile: Optional[StudentProfile] = None
        self.init_ui()
        self.refresh_profile_badge()

    def init_ui(self) -> None:
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # -------------------------------------------------------------
        # 1. SIDEBAR
        # -------------------------------------------------------------
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 16)
        sidebar_layout.setSpacing(6)

        # Brand Header
        brand_box = QVBoxLayout()
        brand_box.setContentsMargins(8, 0, 8, 16)
        brand_box.setSpacing(2)

        brand_title = QLabel("CAREER\nADVISOR")
        brand_title.setObjectName("brandTitle")
        brand_sub = QLabel("Student Readiness Studio")
        brand_sub.setObjectName("brandSubtitle")
        brand_box.addWidget(brand_title)
        brand_box.addWidget(brand_sub)
        sidebar_layout.addLayout(brand_box)

        # Navigation Buttons Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_buttons: List[QPushButton] = []
        nav_items = [
            ("📊 Dashboard", 0),
            ("👤 My Profile", 1),
            ("🧭 Career Guide", 2),
            ("🗺️ Roadmap", 3),
            ("📄 Resume Studio", 4),
            ("📚 Learning Hub", 5),
            ("⚙️ Settings", 6),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, idx=index: self.switch_page(idx))
            self.nav_group.addButton(btn, index)
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Sidebar Footer: Local Offline Status
        footer_card = QFrame()
        footer_card.setStyleSheet(f"""
            background-color: {COLORS.BG_CARD};
            border: 1px solid {COLORS.BORDER};
            border-radius: 8px;
            padding: 8px;
        """)
        f_lay = QHBoxLayout(footer_card)
        f_lay.setContentsMargins(6, 4, 6, 4)
        f_lay.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {COLORS.SUCCESS}; font-size: 14px;")
        status_lbl = QLabel("Local Offline Mode")
        status_lbl.setStyleSheet(f"color: {COLORS.TEXT_MUTED}; font-size: 11px; font-weight: 600;")
        f_lay.addWidget(dot)
        f_lay.addWidget(status_lbl)
        f_lay.addStretch()

        sidebar_layout.addWidget(footer_card)
        root_layout.addWidget(sidebar)

        # -------------------------------------------------------------
        # 2. MAIN CONTENT AREA
        # -------------------------------------------------------------
        main_area = QWidget()
        main_area_layout = QVBoxLayout(main_area)
        main_area_layout.setContentsMargins(0, 0, 0, 0)
        main_area_layout.setSpacing(0)

        # Header Bar
        header_bar = QWidget()
        header_bar.setObjectName("headerBar")
        h_layout = QHBoxLayout(header_bar)
        h_layout.setContentsMargins(24, 12, 24, 12)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self.page_title_lbl = QLabel("Dashboard")
        self.page_title_lbl.setObjectName("pageTitle")
        self.page_sub_lbl = QLabel("Overview of your career match, readiness, roadmap, and resume ATS score.")
        self.page_sub_lbl.setObjectName("pageSubtitle")
        title_box.addWidget(self.page_title_lbl)
        title_box.addWidget(self.page_sub_lbl)
        h_layout.addLayout(title_box)

        h_layout.addStretch()

        # Active Profile Badge
        self.profile_badge = QPushButton("👤 Profile: Loading...")
        self.profile_badge.setStyleSheet(f"""
            background-color: {COLORS.BG_CARD};
            border: 1px solid {COLORS.BORDER};
            border-radius: 20px;
            padding: 6px 14px;
            color: {COLORS.PRIMARY_LIGHT};
            font-size: 12px;
            font-weight: 600;
        """)
        self.profile_badge.setCursor(Qt.PointingHandCursor)
        self.profile_badge.clicked.connect(lambda: self.switch_page(1))
        h_layout.addWidget(self.profile_badge)

        main_area_layout.addWidget(header_bar)

        # Stacked Pages
        self.stacked_widget = QStackedWidget()

        # 0. Dashboard View
        self.dashboard_view = DashboardView()
        self.dashboard_view.navigate_to_profile.connect(lambda: self.switch_page(1))
        self.dashboard_view.navigate_to_career.connect(lambda: self.switch_page(2))
        self.dashboard_view.navigate_to_roadmap.connect(self._navigate_to_roadmap_target)
        self.dashboard_view.navigate_to_resume.connect(self._navigate_to_resume_target)
        self.dashboard_view.navigate_to_learning.connect(lambda: self.switch_page(5))
        self.stacked_widget.addWidget(self.dashboard_view)

        # 1. Profile View
        self.profile_view = ProfileView()
        self.profile_view.profile_saved.connect(self._on_profile_saved)
        self.stacked_widget.addWidget(self.profile_view)

        # 2. Career Assessment View
        self.assessment_view = AssessmentView()
        self.assessment_view.request_roadmap.connect(self._navigate_to_roadmap_target)
        self.assessment_view.request_resume.connect(self._navigate_to_resume_target)
        self.assessment_view.request_learning.connect(self._navigate_to_learning_target)
        self.stacked_widget.addWidget(self.assessment_view)

        # 3. Roadmap View
        self.roadmap_view = RoadmapView()
        self.roadmap_view.progress_changed.connect(lambda _: self.dashboard_view.refresh_dashboard())
        self.stacked_widget.addWidget(self.roadmap_view)

        # 4. Resume Studio View
        self.resume_view = ResumeView()
        self.resume_view.ats_score_changed.connect(lambda _: self.dashboard_view.refresh_dashboard())
        self.stacked_widget.addWidget(self.resume_view)

        # 5. Learning Hub View
        self.learning_view = LearningView()
        self.stacked_widget.addWidget(self.learning_view)

        # 6. Settings View
        self.settings_view = SettingsView()
        self.settings_view.data_reset.connect(self._on_global_data_reset)
        self.stacked_widget.addWidget(self.settings_view)

        main_area_layout.addWidget(self.stacked_widget, stretch=1)
        root_layout.addWidget(main_area, stretch=1)

        # Set default active page (Dashboard)
        self.switch_page(0)

    def switch_page(self, index: int) -> None:
        self.stacked_widget.setCurrentIndex(index)
        if index < len(self.nav_buttons):
            self.nav_buttons[index].setChecked(True)

        titles = [
            ("Dashboard", "Overview of your career match, readiness, roadmap, and resume ATS score."),
            ("My Profile", "Configure your degree, technical skills, interests, and weekly study hours."),
            ("Career Guide", "Explore deterministic match scores and deep dive into skill gaps for 12+ careers."),
            ("Roadmap Planner", "Step-by-step 4-phase weekly roadmap scheduled according to your study capacity."),
            ("Resume Studio", "Build and export ATS-optimized resumes tailored to your target career."),
            ("Learning Hub", "Offline repository of courses, documentation, and exercises mapped to skill gaps."),
            ("Settings & Diagnostics", "System paths, scoring formulas, demo profile loading, and offline diagnostics.")
        ]

        if index < len(titles):
            t, s = titles[index]
            self.page_title_lbl.setText(t)
            self.page_sub_lbl.setText(s)

        if index == 0:
            self.dashboard_view.refresh_dashboard()
        elif index == 2:
            self.assessment_view.run_analysis()
        elif index == 3:
            self.roadmap_view.reload_data()
        elif index == 4:
            self.resume_view.load_or_generate_resume()
        elif index == 5:
            self.learning_view.reload_resources()

    def refresh_profile_badge(self, profile: Optional[StudentProfile] = None) -> None:
        if profile is not None:
            self.current_profile = profile
        else:
            self.current_profile = ProfileRepository.get_profile()

        if self.current_profile and self.current_profile.name.strip():
            self.profile_badge.setText(f"👤 {self.current_profile.name} ({self.current_profile.career_goal})")
        else:
            self.profile_badge.setText("👤 Incomplete Profile (Click to Setup)")

    def _on_profile_saved(self, profile: StudentProfile) -> None:
        self.current_profile = profile
        self.refresh_profile_badge(profile)
        self.dashboard_view.refresh_dashboard()
        self.assessment_view.run_analysis()
        self.roadmap_view.reload_data()
        self.resume_view.load_or_generate_resume()
        self.learning_view.reload_resources()

    def _on_global_data_reset(self) -> None:
        self.refresh_profile_badge()
        self.profile_view.load_profile_data()
        self.dashboard_view.refresh_dashboard()
        self.assessment_view.run_analysis()
        self.roadmap_view.reload_data()
        self.resume_view.load_or_generate_resume()
        self.learning_view.reload_resources()

    def _navigate_to_roadmap_target(self, career_id: str) -> None:
        self.switch_page(3)
        if career_id:
            self.roadmap_view.set_target_career(career_id)

    def _navigate_to_resume_target(self, career_id: str) -> None:
        self.switch_page(4)
        if career_id:
            self.resume_view.set_target_career(career_id)

    def _navigate_to_learning_target(self, skill_or_career: str) -> None:
        self.switch_page(5)
        if skill_or_career:
            self.learning_view.filter_by_skill_tag(skill_or_career)
