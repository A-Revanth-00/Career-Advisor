from __future__ import annotations
from typing import Dict, List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFrame, QScrollArea, QCheckBox, QProgressBar, QTabWidget,
    QGridLayout, QMessageBox
)
from app.core.config import COLORS
from app.career.career_data import Career, load_career_database, get_career_by_id, get_career_by_name
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository
from app.roadmap.roadmap_generator import Roadmap, RoadmapGenerator, RoadmapTask
from app.roadmap.planner import RoadmapPlanner, WeeklyPlan
from app.roadmap.progress import RoadmapProgressTracker, RoadmapProgressState

class TaskCard(QFrame):
    task_toggled = Signal(str, bool)  # task_id, completed

    def __init__(self, task: RoadmapTask, is_completed: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.task = task
        self.is_completed = is_completed
        self.setProperty("class", "card")
        self.init_ui()

    def init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(14)

        # Checkbox
        self.chk = QCheckBox()
        self.chk.setChecked(self.is_completed)
        self.chk.setCursor(Qt.PointingHandCursor)
        self.chk.toggled.connect(lambda checked: self.task_toggled.emit(self.task.id, checked))
        layout.addWidget(self.chk, alignment=Qt.AlignTop)

        # Info Box
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Top line: Title + Category + Priority + Hours
        top_line = QHBoxLayout()
        top_line.setSpacing(8)

        title_lbl = QLabel(self.task.title)
        title_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLORS.TEXT_MAIN};")
        top_line.addWidget(title_lbl)

        # Skill badge
        skill_badge = QLabel(f" {self.task.skill} ")
        skill_badge.setStyleSheet(f"""
            background-color: {COLORS.PRIMARY_MUTED};
            color: {COLORS.PRIMARY_LIGHT};
            border-radius: 6px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: 600;
        """)
        top_line.addWidget(skill_badge)

        top_line.addStretch()

        # Priority tag
        prio_color = COLORS.DANGER if self.task.priority == "High" else COLORS.WARNING if self.task.priority == "Medium" else COLORS.SUCCESS
        prio_badge = QLabel(f"Priority: {self.task.priority}")
        prio_badge.setStyleSheet(f"font-size: 11px; color: {prio_color}; font-weight: 700;")
        top_line.addWidget(prio_badge)

        # Hours badge
        hrs_lbl = QLabel(f"⏱ {self.task.estimated_hours}h")
        hrs_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLORS.TEXT_MUTED};")
        top_line.addWidget(hrs_lbl)

        info_layout.addLayout(top_line)

        # Description
        desc_lbl = QLabel(self.task.description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS.TEXT_MUTED}; line-height: 1.4;")
        info_layout.addWidget(desc_lbl)

        layout.addLayout(info_layout, stretch=1)

class RoadmapView(QWidget):
    progress_changed = Signal(float)  # current progress percentage

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_profile: Optional[StudentProfile] = None
        self.current_career: Optional[Career] = None
        self.current_roadmap: Optional[Roadmap] = None
        self.current_plan: Optional[WeeklyPlan] = None
        self.current_progress: Optional[RoadmapProgressState] = None
        self.init_ui()
        self.reload_data()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(16)

        # 1. Header & Career Selector Card
        header_card = QFrame()
        header_card.setProperty("class", "card")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(12)

        top_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_lbl = QLabel("Personalized Career Roadmap & Weekly Study Planner")
        title_lbl.setProperty("class", "card-title")
        sub_lbl = QLabel("Structured across 4 phases: Foundation, Core Skills, Portfolio Projects, and Career Preparation.")
        sub_lbl.setProperty("class", "card-subtitle")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        top_row.addLayout(title_box)

        top_row.addStretch()

        # Career Goal selector
        sel_box = QHBoxLayout()
        sel_box.setSpacing(8)
        sel_lbl = QLabel("Target Career:")
        sel_lbl.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.career_combo = QComboBox()
        self.career_combo.setMinimumWidth(220)
        self.career_combo.currentIndexChanged.connect(self._on_career_changed)
        sel_box.addWidget(sel_lbl)
        sel_box.addWidget(self.career_combo)
        top_row.addLayout(sel_box)

        h_layout.addLayout(top_row)

        # Summary Metrics Row
        self.metrics_row = QHBoxLayout()
        self.metrics_row.setSpacing(20)

        self.tot_hours_lbl = QLabel("⏱ Total: -- Hours")
        self.tot_hours_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {COLORS.PRIMARY_LIGHT};")

        self.tot_weeks_lbl = QLabel("📅 Duration: -- Weeks")
        self.tot_weeks_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {COLORS.ACCENT_LIGHT};")

        self.pace_lbl = QLabel("⚡ Weekly Pace: -- hrs/wk")
        self.pace_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {COLORS.TEXT_MUTED};")

        self.metrics_row.addWidget(self.tot_hours_lbl)
        self.metrics_row.addWidget(self.tot_weeks_lbl)
        self.metrics_row.addWidget(self.pace_lbl)
        self.metrics_row.addStretch()

        self.reset_btn = QPushButton("Reset Progress")
        self.reset_btn.setProperty("class", "btn-secondary")
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.reset_progress)
        self.metrics_row.addWidget(self.reset_btn)

        h_layout.addLayout(self.metrics_row)

        # Progress bar
        p_row = QVBoxLayout()
        p_row.setSpacing(4)
        self.progress_readout = QLabel("Overall Completion: 0% (0.0 / 0.0 Hours Completed)")
        self.progress_readout.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS.TEXT_MAIN};")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        p_row.addWidget(self.progress_readout)
        p_row.addWidget(self.progress_bar)
        h_layout.addLayout(p_row)

        main_layout.addWidget(header_card)

        # 2. View Mode Tabs (Phased Breakdown vs Weekly Planner)
        self.tabs = QTabWidget()
        
        # Tab 1: Phased View
        self.phase_tab = QWidget()
        phase_tab_layout = QVBoxLayout(self.phase_tab)
        phase_tab_layout.setContentsMargins(12, 12, 12, 12)
        
        phase_scroll = QScrollArea()
        phase_scroll.setWidgetResizable(True)
        phase_scroll.setFrameShape(QFrame.NoFrame)
        phase_scroll.setStyleSheet("background: transparent;")
        
        self.phase_container = QWidget()
        self.phase_layout = QVBoxLayout(self.phase_container)
        self.phase_layout.setContentsMargins(0, 0, 0, 0)
        self.phase_layout.setSpacing(16)
        
        phase_scroll.setWidget(self.phase_container)
        phase_tab_layout.addWidget(phase_scroll)
        self.tabs.addTab(self.phase_tab, "🗺️ Phased Roadmap (All 4 Phases)")

        # Tab 2: Weekly Schedule View
        self.weekly_tab = QWidget()
        weekly_tab_layout = QVBoxLayout(self.weekly_tab)
        weekly_tab_layout.setContentsMargins(12, 12, 12, 12)
        
        weekly_scroll = QScrollArea()
        weekly_scroll.setWidgetResizable(True)
        weekly_scroll.setFrameShape(QFrame.NoFrame)
        weekly_scroll.setStyleSheet("background: transparent;")
        
        self.weekly_container = QWidget()
        self.weekly_layout = QVBoxLayout(self.weekly_container)
        self.weekly_layout.setContentsMargins(0, 0, 0, 0)
        self.weekly_layout.setSpacing(14)
        
        weekly_scroll.setWidget(self.weekly_container)
        weekly_tab_layout.addWidget(weekly_scroll)
        self.tabs.addTab(self.weekly_tab, "📅 Weekly Learning Schedule")

        main_layout.addWidget(self.tabs, stretch=1)

    def set_target_career(self, career_id_or_name: str) -> None:
        """External slot to switch target career from Career Guide or Dashboard."""
        career = get_career_by_id(career_id_or_name) or get_career_by_name(career_id_or_name)
        if career:
            idx = self.career_combo.findData(career.id)
            if idx >= 0:
                self.career_combo.setCurrentIndex(idx)

    def reload_data(self) -> None:
        self.current_profile = ProfileRepository.get_profile() or StudentProfile()
        
        # Populate career combo
        careers = load_career_database()
        self.career_combo.blockSignals(True)
        self.career_combo.clear()
        selected_idx = 0
        for i, c in enumerate(careers):
            self.career_combo.addItem(c.name, c.id)
            if self.current_profile and (c.name.lower() == self.current_profile.career_goal.lower() or c.id == self.current_profile.career_goal):
                selected_idx = i
        self.career_combo.setCurrentIndex(selected_idx)
        self.career_combo.blockSignals(False)

        self._regenerate_and_render()

    def _on_career_changed(self) -> None:
        self._regenerate_and_render()

    def _regenerate_and_render(self) -> None:
        career_id = self.career_combo.currentData()
        if not career_id:
            careers = load_career_database()
            if careers:
                career_id = careers[0].id
            else:
                return

        self.current_career = get_career_by_id(career_id)
        if not self.current_career:
            return

        if not self.current_profile:
            self.current_profile = ProfileRepository.get_profile() or StudentProfile()

        # Generate roadmap
        self.current_roadmap = RoadmapGenerator.generate(self.current_profile, self.current_career)
        self.current_plan = RoadmapPlanner.plan(
            self.current_roadmap,
            self.current_profile.hours_per_day,
            self.current_profile.days_per_week
        )
        self.current_progress = RoadmapProgressTracker.get_progress(self.current_roadmap)

        # Update metrics readout
        self.tot_hours_lbl.setText(f"⏱ Total: {self.current_roadmap.total_hours} Hours")
        self.tot_weeks_lbl.setText(f"📅 Duration: {self.current_plan.total_estimated_weeks} Weeks")
        self.pace_lbl.setText(f"⚡ Study Pace: {self.current_plan.weekly_hours_capacity} hrs/wk")
        self._update_progress_ui()

        # Render Phased View
        self._render_phased_view()

        # Render Weekly View
        self._render_weekly_view()

    def _update_progress_ui(self) -> None:
        if not self.current_roadmap:
            return
        self.current_progress = RoadmapProgressTracker.get_progress(self.current_roadmap)
        p = self.current_progress
        self.progress_bar.setValue(int(p.percentage))
        self.progress_readout.setText(
            f"Overall Completion: {p.percentage}% "
            f"({p.completed_hours} / {p.total_hours} Hours • {p.completed_tasks_count}/{p.total_tasks} Tasks)"
        )
        self.progress_changed.emit(p.percentage)

    def _render_phased_view(self) -> None:
        # Clear existing
        while self.phase_layout.count():
            item = self.phase_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.current_roadmap or not self.current_progress:
            return

        phases_map = {
            1: ("Phase 1: Foundation (Prerequisites & Concepts)", self.current_roadmap.phase_1_tasks),
            2: ("Phase 2: Core Skills (Frameworks & Libraries)", self.current_roadmap.phase_2_tasks),
            3: ("Phase 3: Projects (Hands-on Portfolio Capstones)", self.current_roadmap.phase_3_tasks),
            4: ("Phase 4: Career Preparation (Resume & Interviews)", self.current_roadmap.phase_4_tasks)
        }

        for p_num, (p_title, tasks) in phases_map.items():
            if not tasks:
                continue

            card = QFrame()
            card.setProperty("class", "card")
            c_layout = QVBoxLayout(card)
            c_layout.setSpacing(10)

            # Phase header
            p_header = QHBoxLayout()
            title_lbl = QLabel(p_title)
            title_lbl.setProperty("class", "card-title")
            p_header.addWidget(title_lbl)

            p_pct = self.current_progress.phase_progress.get(p_num, 0.0)
            p_badge = QLabel(f" {p_pct}% Complete ")
            p_badge.setStyleSheet(f"""
                background-color: {COLORS.SUCCESS_BG if p_pct >= 100 else COLORS.PRIMARY_MUTED};
                color: {COLORS.SUCCESS if p_pct >= 100 else COLORS.PRIMARY_LIGHT};
                border-radius: 8px;
                padding: 2px 8px;
                font-weight: 700;
                font-size: 11px;
            """)
            p_header.addStretch()
            p_header.addWidget(p_badge)
            c_layout.addLayout(p_header)

            # Add tasks
            for task in tasks:
                is_comp = task.id in self.current_progress.completed_task_ids
                t_card = TaskCard(task, is_comp)
                t_card.task_toggled.connect(self._on_task_toggled)
                c_layout.addWidget(t_card)

            self.phase_layout.addWidget(card)

    def _render_weekly_view(self) -> None:
        # Clear existing
        while self.weekly_layout.count():
            item = self.weekly_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.current_plan or not self.current_progress:
            return

        for w in self.current_plan.weeks:
            w_card = QFrame()
            w_card.setProperty("class", "card")
            w_layout = QVBoxLayout(w_card)
            w_layout.setSpacing(8)

            w_header = QHBoxLayout()
            w_title = QLabel(f"Week {w.week_number} Schedule")
            w_title.setProperty("class", "card-title")
            w_header.addWidget(w_title)

            w_header.addStretch()
            w_hrs = QLabel(f"Study Load: <b>{w.total_allocated_hours} / {w.max_weekly_hours} Hours</b>")
            w_hrs.setStyleSheet(f"font-size: 12px; color: {COLORS.PRIMARY_LIGHT};")
            w_header.addWidget(w_hrs)
            w_layout.addLayout(w_header)

            for alloc in w.allocations:
                item_row = QHBoxLayout()
                item_row.setSpacing(10)
                is_comp = alloc.task.id in self.current_progress.completed_task_ids
                
                chk = QCheckBox()
                chk.setChecked(is_comp)
                chk.toggled.connect(lambda checked, tid=alloc.task.id: self._on_task_toggled(tid, checked))
                item_row.addWidget(chk)

                lbl_txt = f"<b>{alloc.task.title}</b> {alloc.part_info} &bull; <span style='color: {COLORS.TEXT_MUTED};'>({alloc.task.skill})</span>"
                task_lbl = QLabel(lbl_txt)
                task_lbl.setStyleSheet(f"font-size: 13px; color: {COLORS.TEXT_MAIN};")
                item_row.addWidget(task_lbl, stretch=1)

                h_alloc_lbl = QLabel(f"{alloc.allocated_hours}h allocated")
                h_alloc_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_SUBTLE}; font-weight: 600;")
                item_row.addWidget(h_alloc_lbl)

                w_layout.addLayout(item_row)

            self.weekly_layout.addWidget(w_card)

    def _on_task_toggled(self, task_id: str, completed: bool) -> None:
        if not self.current_career:
            return
        RoadmapProgressTracker.set_task_completed(self.current_career.id, task_id, completed)
        self._update_progress_ui()

    def reset_progress(self) -> None:
        if not self.current_career:
            return
        reply = QMessageBox.question(
            self, "Reset Roadmap Progress",
            f"Are you sure you want to reset all completed tasks for {self.current_career.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            RoadmapProgressTracker.reset_career_progress(self.current_career.id)
            self._regenerate_and_render()
