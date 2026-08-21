from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QPushButton, QFrame, QMessageBox,
    QScrollArea, QGridLayout, QSizePolicy
)
from app.core.config import COLORS
from app.core.utils import parse_comma_separated, format_list_as_comma, validate_cgpa, validate_hours_and_days
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository
from app.career.career_data import load_career_database

class ProfileView(QWidget):
    profile_saved = Signal(StudentProfile)

    QUICK_SKILLS = [
        "Python", "JavaScript", "SQL", "Git", "React", "Node.js", "C++",
        "Java", "TypeScript", "PyTorch", "Docker", "AWS", "FastAPI",
        "Data Structures", "Algorithms", "Pandas", "Scikit-Learn", "HTML5", "CSS3"
    ]

    QUICK_INTERESTS = [
        "Artificial Intelligence", "Web Development", "Data Science",
        "Cybersecurity", "Cloud Computing", "Mobile Apps", "System Design",
        "DevOps", "Machine Learning", "Algorithms"
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.load_profile_data()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(16)

        # Header banner
        header_card = QFrame()
        header_card.setProperty("class", "card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)

        info_box = QVBoxLayout()
        title_lbl = QLabel("Student Profile & Academic Background")
        title_lbl.setProperty("class", "card-title")
        sub_lbl = QLabel("Your profile parameters drive deterministic career matching, skill gap analysis, and roadmap scheduling.")
        sub_lbl.setProperty("class", "card-subtitle")
        info_box.addWidget(title_lbl)
        info_box.addWidget(sub_lbl)
        h_layout.addLayout(info_box)

        self.save_btn_top = QPushButton("💾 Save Profile")
        self.save_btn_top.setProperty("class", "btn-primary")
        self.save_btn_top.setCursor(Qt.PointingHandCursor)
        self.save_btn_top.clicked.connect(self.save_profile)
        h_layout.addWidget(self.save_btn_top, alignment=Qt.AlignRight | Qt.AlignVCenter)

        main_layout.addWidget(header_card)

        # Scrollable form container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)

        # 1. Personal & Contact Card
        personal_card = QFrame()
        personal_card.setProperty("class", "card")
        p_layout = QVBoxLayout(personal_card)
        p_layout.setSpacing(12)

        sec_title1 = QLabel("1. Personal Information")
        sec_title1.setProperty("class", "card-title")
        p_layout.addWidget(sec_title1)

        p_grid = QGridLayout()
        p_grid.setHorizontalSpacing(16)
        p_grid.setVerticalSpacing(8)

        lbl_name = QLabel("Full Name *")
        lbl_name.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. Alex Rivera")

        lbl_email = QLabel("Email Address *")
        lbl_email.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("e.g. alex.rivera@cs.edu")

        p_grid.addWidget(lbl_name, 0, 0)
        p_grid.addWidget(self.name_edit, 1, 0)
        p_grid.addWidget(lbl_email, 0, 1)
        p_grid.addWidget(self.email_edit, 1, 1)

        p_layout.addLayout(p_grid)
        form_layout.addWidget(personal_card)

        # 2. Education Card
        edu_card = QFrame()
        edu_card.setProperty("class", "card")
        e_layout = QVBoxLayout(edu_card)
        e_layout.setSpacing(12)

        sec_title2 = QLabel("2. Academic Details")
        sec_title2.setProperty("class", "card-title")
        e_layout.addWidget(sec_title2)

        e_grid = QGridLayout()
        e_grid.setHorizontalSpacing(16)
        e_grid.setVerticalSpacing(8)

        lbl_deg = QLabel("Degree / Program *")
        lbl_deg.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.degree_combo = QComboBox()
        self.degree_combo.addItems(["B.Tech", "B.E.", "BCA", "MCA", "B.Sc (Computer Science)", "M.Tech", "M.Sc (Data Science)", "Other"])
        self.degree_combo.setEditable(True)

        lbl_branch = QLabel("Major / Branch *")
        lbl_branch.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.branch_combo = QComboBox()
        self.branch_combo.addItems([
            "Computer Science", "Information Technology", "Artificial Intelligence & Data Science",
            "Software Engineering", "Electronics & Communication", "Data Science", "Computer Applications"
        ])
        self.branch_combo.setEditable(True)

        lbl_cgpa = QLabel("CGPA / GPA (Scale 0-10) *")
        lbl_cgpa.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.cgpa_spin = QDoubleSpinBox()
        self.cgpa_spin.setRange(0.0, 10.0)
        self.cgpa_spin.setSingleStep(0.1)
        self.cgpa_spin.setValue(8.5)

        e_grid.addWidget(lbl_deg, 0, 0)
        e_grid.addWidget(self.degree_combo, 1, 0)
        e_grid.addWidget(lbl_branch, 0, 1)
        e_grid.addWidget(self.branch_combo, 1, 1)
        e_grid.addWidget(lbl_cgpa, 0, 2)
        e_grid.addWidget(self.cgpa_spin, 1, 2)

        e_layout.addLayout(e_grid)
        form_layout.addWidget(edu_card)

        # 3. Skills & Interests Card
        skills_card = QFrame()
        skills_card.setProperty("class", "card")
        s_layout = QVBoxLayout(skills_card)
        s_layout.setSpacing(12)

        sec_title3 = QLabel("3. Technical Skills & Interests")
        sec_title3.setProperty("class", "card-title")
        s_layout.addWidget(sec_title3)

        # Skills Input
        lbl_skills = QLabel("Technical Skills (comma-separated) *")
        lbl_skills.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.skills_edit = QLineEdit()
        self.skills_edit.setPlaceholderText("e.g. Python, SQL, Git, React, Docker")
        s_layout.addWidget(lbl_skills)
        s_layout.addWidget(self.skills_edit)

        # Quick Skill Chips
        chip_lbl1 = QLabel("Quick Add Popular Skills:")
        chip_lbl1.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_SUBTLE}; font-weight: 600;")
        s_layout.addWidget(chip_lbl1)

        chips_layout1 = QHBoxLayout()
        chips_layout1.setSpacing(6)
        for sk in self.QUICK_SKILLS[:10]:
            btn = QPushButton(f"+ {sk}")
            btn.setProperty("class", "chip-btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, s=sk: self.add_skill_tag(s))
            chips_layout1.addWidget(btn)
        chips_layout1.addStretch()
        s_layout.addLayout(chips_layout1)

        # Interests Input
        lbl_interests = QLabel("Career Interests & Passions (comma-separated)")
        lbl_interests.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED}; margin-top: 8px;")
        self.interests_edit = QLineEdit()
        self.interests_edit.setPlaceholderText("e.g. Artificial Intelligence, System Design, Automation")
        s_layout.addWidget(lbl_interests)
        s_layout.addWidget(self.interests_edit)

        # Quick Interest Chips
        chip_lbl2 = QLabel("Quick Add Interests:")
        chip_lbl2.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_SUBTLE}; font-weight: 600;")
        s_layout.addWidget(chip_lbl2)

        chips_layout2 = QHBoxLayout()
        chips_layout2.setSpacing(6)
        for it in self.QUICK_INTERESTS[:8]:
            btn = QPushButton(f"+ {it}")
            btn.setProperty("class", "chip-btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, i=it: self.add_interest_tag(i))
            chips_layout2.addWidget(btn)
        chips_layout2.addStretch()
        s_layout.addLayout(chips_layout2)

        form_layout.addWidget(skills_card)

        # 4. Career Goal & Study Availability Card
        plan_card = QFrame()
        plan_card.setProperty("class", "card")
        pl_layout = QVBoxLayout(plan_card)
        pl_layout.setSpacing(12)

        sec_title4 = QLabel("4. Target Career & Learning Availability")
        sec_title4.setProperty("class", "card-title")
        pl_layout.addWidget(sec_title4)

        pl_grid = QGridLayout()
        pl_grid.setHorizontalSpacing(16)
        pl_grid.setVerticalSpacing(8)

        lbl_goal = QLabel("Primary Career Target *")
        lbl_goal.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.goal_combo = QComboBox()
        self._populate_careers_combo()

        lbl_hours = QLabel("Study Hours / Day *")
        lbl_hours.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(0.5, 16.0)
        self.hours_spin.setSingleStep(0.5)
        self.hours_spin.setValue(2.0)
        self.hours_spin.valueChanged.connect(self._update_weekly_hours_label)

        lbl_days = QLabel("Study Days / Week *")
        lbl_days.setStyleSheet(f"font-weight: 600; color: {COLORS.TEXT_MUTED};")
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 7)
        self.days_spin.setValue(5)
        self.days_spin.valueChanged.connect(self._update_weekly_hours_label)

        pl_grid.addWidget(lbl_goal, 0, 0)
        pl_grid.addWidget(self.goal_combo, 1, 0)
        pl_grid.addWidget(lbl_hours, 0, 1)
        pl_grid.addWidget(self.hours_spin, 1, 1)
        pl_grid.addWidget(lbl_days, 0, 2)
        pl_grid.addWidget(self.days_spin, 1, 2)

        pl_layout.addLayout(pl_grid)

        # Weekly Hours Readout Banner
        self.weekly_hours_banner = QLabel()
        self.weekly_hours_banner.setStyleSheet(f"""
            background-color: {COLORS.PRIMARY_MUTED};
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            padding: 8px 12px;
            color: {COLORS.PRIMARY_LIGHT};
            font-weight: 600;
            font-size: 12px;
        """)
        self._update_weekly_hours_label()
        pl_layout.addWidget(self.weekly_hours_banner)

        form_layout.addWidget(plan_card)

        # Action Buttons Bottom
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        self.reset_btn = QPushButton("Reset Defaults")
        self.reset_btn.setProperty("class", "btn-secondary")
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.reset_defaults)
        action_layout.addWidget(self.reset_btn)

        action_layout.addStretch()

        self.save_btn_bottom = QPushButton("💾 Save & Update Profile")
        self.save_btn_bottom.setProperty("class", "btn-primary")
        self.save_btn_bottom.setCursor(Qt.PointingHandCursor)
        self.save_btn_bottom.clicked.connect(self.save_profile)
        action_layout.addWidget(self.save_btn_bottom)

        form_layout.addLayout(action_layout)

        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)

    def _populate_careers_combo(self) -> None:
        careers = load_career_database()
        self.goal_combo.clear()
        if careers:
            for c in careers:
                self.goal_combo.addItem(c.name, c.id)
        else:
            self.goal_combo.addItems([
                "AI Engineer", "Software Developer", "Backend Developer",
                "Frontend Developer", "Data Scientist", "Cybersecurity Engineer",
                "Cloud Engineer", "DevOps Engineer", "Mobile Developer",
                "Full Stack Developer", "Data Analyst", "Machine Learning Engineer"
            ])

    def _update_weekly_hours_label(self) -> None:
        total = round(self.hours_spin.value() * self.days_spin.value(), 1)
        self.weekly_hours_banner.setText(f"📅 Total Learning Capacity: {total} Hours / Week ({self.hours_spin.value()} hrs/day × {self.days_spin.value()} days/week)")

    def add_skill_tag(self, skill: str) -> None:
        current = parse_comma_separated(self.skills_edit.text())
        if skill not in current:
            current.append(skill)
            self.skills_edit.setText(format_list_as_comma(current))

    def add_interest_tag(self, interest: str) -> None:
        current = parse_comma_separated(self.interests_edit.text())
        if interest not in current:
            current.append(interest)
            self.interests_edit.setText(format_list_as_comma(current))

    def load_profile_data(self) -> None:
        profile = ProfileRepository.get_profile()
        if profile:
            self.name_edit.setText(profile.name)
            self.email_edit.setText(profile.email)
            self.degree_combo.setCurrentText(profile.education)
            self.branch_combo.setCurrentText(profile.branch)
            self.cgpa_spin.setValue(profile.cgpa)
            self.skills_edit.setText(profile.skills_csv)
            self.interests_edit.setText(profile.interests_csv)
            
            idx = self.goal_combo.findText(profile.career_goal, Qt.MatchContains)
            if idx >= 0:
                self.goal_combo.setCurrentIndex(idx)
            else:
                self.goal_combo.setEditText(profile.career_goal)
                
            self.hours_spin.setValue(profile.hours_per_day)
            self.days_spin.setValue(profile.days_per_week)
            self._update_weekly_hours_label()

    def save_profile(self) -> None:
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        degree = self.degree_combo.currentText().strip()
        branch = self.branch_combo.currentText().strip()
        cgpa_val = self.cgpa_spin.value()
        skills = parse_comma_separated(self.skills_edit.text())
        interests = parse_comma_separated(self.interests_edit.text())
        career_goal = self.goal_combo.currentText().strip()
        hours = self.hours_spin.value()
        days = self.days_spin.value()

        # Validation
        if not name:
            QMessageBox.warning(self, "Validation Error", "Full Name is required to save your profile.")
            self.name_edit.setFocus()
            return

        if not email or "@" not in email:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address.")
            self.email_edit.setFocus()
            return

        if not skills:
            QMessageBox.warning(self, "Validation Error", "Please enter at least one technical skill to enable career matching.")
            self.skills_edit.setFocus()
            return

        valid_cgpa, cgpa_clean, cgpa_msg = validate_cgpa(cgpa_val)
        if not valid_cgpa:
            QMessageBox.warning(self, "Validation Error", cgpa_msg)
            return

        valid_avail, h_clean, d_clean, avail_msg = validate_hours_and_days(hours, days)
        if not valid_avail:
            QMessageBox.warning(self, "Validation Error", avail_msg)
            return

        profile = StudentProfile(
            name=name,
            email=email,
            education=degree,
            branch=branch,
            cgpa=cgpa_clean,
            skills=skills,
            interests=interests,
            career_goal=career_goal,
            hours_per_day=h_clean,
            days_per_week=d_clean
        )

        try:
            saved = ProfileRepository.save_or_update_profile(profile)
            self.profile_saved.emit(saved)
            QMessageBox.information(
                self, "Profile Saved",
                f"Student Profile for {saved.name} saved successfully!\n"
                f"Target Career: {saved.career_goal}\n"
                f"Study Availability: {saved.weekly_hours} hrs/week"
            )
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save profile: {e}")

    def reset_defaults(self) -> None:
        reply = QMessageBox.question(
            self, "Reset Profile",
            "Are you sure you want to reset profile fields to default demo values?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.name_edit.setText("Alex Rivera")
            self.email_edit.setText("alex.rivera@cs.edu")
            self.degree_combo.setCurrentText("B.Tech")
            self.branch_combo.setCurrentText("Computer Science")
            self.cgpa_spin.setValue(8.8)
            self.skills_edit.setText("Python, SQL, Git, React, JavaScript, Data Structures")
            self.interests_edit.setText("Artificial Intelligence, Web Development, System Design")
            self.goal_combo.setCurrentText("AI Engineer")
            self.hours_spin.setValue(2.5)
            self.days_spin.setValue(5)
            self._update_weekly_hours_label()
