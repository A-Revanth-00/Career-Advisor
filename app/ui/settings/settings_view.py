from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox
)
from app.core.config import APP_NAME, APP_VERSION, APP_TAGLINE, COLORS
from app.core.paths import DATABASE_PATH, CAREER_DATABASE_PATH, LEARNING_RESOURCES_PATH
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository, RoadmapRepository, ResumeRepository
from app.career.career_data import load_career_database
from app.learning.resource_database import load_learning_resources

class SettingsView(QWidget):
    data_reset = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.init_ui()

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

        # Header Card
        header_card = QFrame()
        header_card.setProperty("class", "card")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(6)

        title_lbl = QLabel(f"{APP_NAME} Settings & System Diagnostics")
        title_lbl.setProperty("class", "card-title")
        sub_lbl = QLabel(f"{APP_TAGLINE} (Version {APP_VERSION})")
        sub_lbl.setProperty("class", "card-subtitle")
        h_layout.addWidget(title_lbl)
        h_layout.addWidget(sub_lbl)
        layout.addWidget(header_card)

        # System & Offline Mode Card
        sys_card = QFrame()
        sys_card.setProperty("class", "card")
        s_layout = QVBoxLayout(sys_card)
        s_layout.setSpacing(10)

        s_title = QLabel("1. Local Architecture & Environment")
        s_title.setProperty("class", "card-title")
        s_layout.addWidget(s_title)

        s_grid = QVBoxLayout()
        s_grid.setSpacing(6)

        s_grid.addWidget(QLabel(f"⚡ <b>Execution Mode:</b> 100% Offline-First (No external API or network dependencies)"))
        s_grid.addWidget(QLabel(f"📁 <b>SQLite Database:</b> <span style='font-family:monospace; color:{COLORS.PRIMARY_LIGHT};'>{DATABASE_PATH}</span>"))
        s_grid.addWidget(QLabel(f"📚 <b>Career Knowledge Base:</b> <span style='font-family:monospace; color:{COLORS.PRIMARY_LIGHT};'>{CAREER_DATABASE_PATH}</span>"))
        s_grid.addWidget(QLabel(f"📖 <b>Learning Resources:</b> <span style='font-family:monospace; color:{COLORS.PRIMARY_LIGHT};'>{LEARNING_RESOURCES_PATH}</span>"))

        s_layout.addLayout(s_grid)
        layout.addWidget(sys_card)

        # Deterministic Scoring Transparency Card
        math_card = QFrame()
        math_card.setProperty("class", "card")
        m_layout = QVBoxLayout(math_card)
        m_layout.setSpacing(10)

        m_title = QLabel("2. Deterministic Scoring Methodology")
        m_title.setProperty("class", "card-title")
        m_layout.addWidget(m_title)

        m_desc = QLabel(
            "<b>Career Match Score Formula:</b><br>"
            "&bull; <b>Skills Match (50%):</b> Direct normalized comparison against required core skills + optional skill bonus.<br>"
            "&bull; <b>Interests Match (35%):</b> Alignment with domain passion areas and industry specializations.<br>"
            "&bull; <b>Education Compatibility (15%):</b> Degree and major compatibility check.<br><br>"
            "<b>Career Readiness Formula:</b><br>"
            "&bull; 60% Skill Gap Ratio + 25% Interest Alignment + 15% Academic Foundation."
        )
        m_desc.setWordWrap(True)
        m_desc.setStyleSheet(f"font-size: 12px; color: {COLORS.TEXT_MUTED}; line-height: 1.5;")
        m_layout.addWidget(m_desc)
        layout.addWidget(math_card)

        # Database Management & Demo Tools Card
        db_card = QFrame()
        db_card.setProperty("class", "card")
        d_layout = QVBoxLayout(db_card)
        d_layout.setSpacing(12)

        d_title = QLabel("3. Database Maintenance & Demo Setup")
        d_title.setProperty("class", "card-title")
        d_layout.addWidget(d_title)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        reload_btn = QPushButton("🔄 Reload Offline Databases")
        reload_btn.setProperty("class", "btn-secondary")
        reload_btn.setCursor(Qt.PointingHandCursor)
        reload_btn.clicked.connect(self.reload_databases)
        btn_row.addWidget(reload_btn)

        demo_btn = QPushButton("🎯 Load Alex Rivera Demo Profile")
        demo_btn.setProperty("class", "btn-secondary")
        demo_btn.setCursor(Qt.PointingHandCursor)
        demo_btn.clicked.connect(self.load_demo_profile)
        btn_row.addWidget(demo_btn)

        btn_row.addStretch()
        d_layout.addLayout(btn_row)
        layout.addWidget(db_card)

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

    def reload_databases(self) -> None:
        c = load_career_database(force_reload=True)
        r = load_learning_resources(force_reload=True)
        QMessageBox.information(
            self, "Databases Reloaded",
            f"Successfully reloaded:\n• {len(c)} Career profiles\n• {len(r)} Learning resources"
        )

    def load_demo_profile(self) -> None:
        reply = QMessageBox.question(
            self, "Load Demo Profile",
            "This will populate the active profile with demo student 'Alex Rivera' (B.Tech CS, AI Engineer target). Proceed?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            demo = StudentProfile(
                name="Alex Rivera",
                email="alex.rivera@cs.edu",
                education="B.Tech",
                branch="Computer Science",
                cgpa=8.8,
                skills=["Python", "SQL", "Git", "React", "JavaScript", "Data Structures"],
                interests=["Artificial Intelligence", "Web Development", "System Design"],
                career_goal="AI Engineer",
                hours_per_day=2.5,
                days_per_week=5
            )
            ProfileRepository.save_or_update_profile(demo)
            self.data_reset.emit()
            QMessageBox.information(self, "Demo Profile Loaded", "Alex Rivera demo profile loaded successfully!")
