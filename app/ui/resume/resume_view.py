from __future__ import annotations
import os
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QFrame, QScrollArea, QTabWidget, QSplitter,
    QMessageBox, QFileDialog, QApplication, QProgressBar, QComboBox
)
from app.core.config import COLORS
from app.core.paths import EXPORTS_DIR
from app.core.utils import parse_comma_separated, format_list_as_comma
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository, ResumeRepository
from app.resume.resume_data import (
    ResumeData, ContactInfo, EducationEntry, ProjectEntry,
    CertificationEntry, AchievementEntry
)
from app.resume.resume_builder import ResumeBuilder, get_available_templates
from app.resume.ats_analyzer import LocalATSAnalyzer, ATSAnalysisResult
from app.ui.resume.resume_preview import ResumePreviewWidget

class ResumeView(QWidget):
    ats_score_changed = Signal(int)  # new ATS score

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_profile: Optional[StudentProfile] = None
        self.current_resume: Optional[ResumeData] = None
        self.ats_result: Optional[ATSAnalysisResult] = None
        self.current_template_id: str = "modern"
        self.init_ui()
        self.load_or_generate_resume()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(14)

        # 1. Header Action Bar
        header_card = QFrame()
        header_card.setProperty("class", "card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setSpacing(12)

        title_box = QVBoxLayout()
        title_lbl = QLabel("Professional Resume Studio & ATS Analyzer")
        title_lbl.setProperty("class", "card-title")
        sub_lbl = QLabel("Auto-tailor professional fresher resumes directly from your student profile and roadmap projects.")
        sub_lbl.setProperty("class", "card-subtitle")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        h_layout.addLayout(title_box)

        h_layout.addStretch()

        # Action Buttons
        self.autogen_btn = QPushButton("⚡ Auto-Generate from Profile")
        self.autogen_btn.setProperty("class", "btn-secondary")
        self.autogen_btn.setCursor(Qt.PointingHandCursor)
        self.autogen_btn.clicked.connect(self.generate_from_current_profile)
        h_layout.addWidget(self.autogen_btn)

        self.save_btn = QPushButton("💾 Save Resume")
        self.save_btn.setProperty("class", "btn-primary")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_resume)
        h_layout.addWidget(self.save_btn)

        main_layout.addWidget(header_card)

        # 2. Main Splitter (Left: Editor Tabs, Right: Live Preview & ATS)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # LEFT PANEL: Editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)

        editor_lbl = QLabel("✏️ Resume Editor")
        editor_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLORS.TEXT_MAIN};")
        left_layout.addWidget(editor_lbl)

        self.editor_tabs = QTabWidget()
        self._init_editor_tabs()
        left_layout.addWidget(self.editor_tabs)

        splitter.addWidget(left_widget)

        # RIGHT PANEL: Preview & ATS Analyzer
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(10)

        # Top ATS Score Drawer
        self.ats_card = QFrame()
        self.ats_card.setProperty("class", "card")
        ats_layout = QVBoxLayout(self.ats_card)
        ats_layout.setSpacing(8)

        ats_hdr = QHBoxLayout()
        ats_title = QLabel("📊 Local ATS Heuristic Score")
        ats_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLORS.TEXT_MAIN};")
        ats_hdr.addWidget(ats_title)

        self.ats_score_badge = QLabel(" 0 / 100 ")
        self.ats_score_badge.setStyleSheet(f"""
            background-color: {COLORS.PRIMARY_MUTED};
            color: {COLORS.PRIMARY_LIGHT};
            border-radius: 8px;
            padding: 3px 8px;
            font-weight: 800;
            font-size: 12px;
        """)
        ats_hdr.addStretch()
        ats_hdr.addWidget(self.ats_score_badge)
        ats_layout.addLayout(ats_hdr)

        self.ats_bar = QProgressBar()
        self.ats_bar.setValue(0)
        ats_layout.addWidget(self.ats_bar)

        self.ats_feedback_lbl = QLabel("Run ATS Analysis to see detailed heuristic screening feedback.")
        self.ats_feedback_lbl.setWordWrap(True)
        self.ats_feedback_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS.TEXT_MUTED};")
        ats_layout.addWidget(self.ats_feedback_lbl)

        right_layout.addWidget(self.ats_card)

        # Live HTML Preview Header
        preview_hdr = QHBoxLayout()
        preview_lbl = QLabel("📄 Live Document Preview")
        preview_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COLORS.TEXT_MAIN};")
        preview_hdr.addWidget(preview_lbl)

        preview_hdr.addStretch()

        tpl_lbl = QLabel("Layout:")
        tpl_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS.TEXT_MUTED}; font-weight: 600;")
        preview_hdr.addWidget(tpl_lbl)

        self.template_combo = QComboBox()
        self.template_combo.setCursor(Qt.PointingHandCursor)
        for t in get_available_templates():
            self.template_combo.addItem(f"🎨 {t['name']}", t["id"])
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        preview_hdr.addWidget(self.template_combo)

        copy_btn = QPushButton("📋 Copy Markdown")
        copy_btn.setProperty("class", "btn-secondary")
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(self.copy_markdown_to_clipboard)
        preview_hdr.addWidget(copy_btn)

        export_html_btn = QPushButton("🌐 Export HTML")
        export_html_btn.setProperty("class", "btn-secondary")
        export_html_btn.setCursor(Qt.PointingHandCursor)
        export_html_btn.clicked.connect(self.export_html_file)
        preview_hdr.addWidget(export_html_btn)

        export_txt_btn = QPushButton("📝 Export Text")
        export_txt_btn.setProperty("class", "btn-secondary")
        export_txt_btn.setCursor(Qt.PointingHandCursor)
        export_txt_btn.clicked.connect(self.export_text_file)
        preview_hdr.addWidget(export_txt_btn)

        right_layout.addLayout(preview_hdr)

        self.preview_widget = ResumePreviewWidget()
        right_layout.addWidget(self.preview_widget, stretch=1)

        splitter.addWidget(right_widget)
        splitter.setSizes([450, 550])

        main_layout.addWidget(splitter, stretch=1)

    def _init_editor_tabs(self) -> None:
        # Tab 1: Contact & Summary
        tab1 = QWidget()
        t1_layout = QVBoxLayout(tab1)
        t1_layout.setContentsMargins(12, 12, 12, 12)
        t1_layout.setSpacing(8)

        t1_layout.addWidget(QLabel("Full Name:"))
        self.ed_name = QLineEdit()
        self.ed_name.textChanged.connect(self._sync_and_preview)
        t1_layout.addWidget(self.ed_name)

        t1_layout.addWidget(QLabel("Email:"))
        self.ed_email = QLineEdit()
        self.ed_email.textChanged.connect(self._sync_and_preview)
        t1_layout.addWidget(self.ed_email)

        t1_layout.addWidget(QLabel("Phone & Location:"))
        h_box1 = QHBoxLayout()
        self.ed_phone = QLineEdit()
        self.ed_phone.textChanged.connect(self._sync_and_preview)
        self.ed_loc = QLineEdit()
        self.ed_loc.textChanged.connect(self._sync_and_preview)
        h_box1.addWidget(self.ed_phone)
        h_box1.addWidget(self.ed_loc)
        t1_layout.addLayout(h_box1)

        t1_layout.addWidget(QLabel("LinkedIn & GitHub Profiles:"))
        h_box2 = QHBoxLayout()
        self.ed_linkedin = QLineEdit()
        self.ed_linkedin.textChanged.connect(self._sync_and_preview)
        self.ed_github = QLineEdit()
        self.ed_github.textChanged.connect(self._sync_and_preview)
        h_box2.addWidget(self.ed_linkedin)
        h_box2.addWidget(self.ed_github)
        t1_layout.addLayout(h_box2)

        t1_layout.addWidget(QLabel("Professional Summary:"))
        self.ed_summary = QTextEdit()
        self.ed_summary.setMinimumHeight(90)
        self.ed_summary.textChanged.connect(self._sync_and_preview)
        t1_layout.addWidget(self.ed_summary)

        self.editor_tabs.addTab(tab1, "👤 Contact & Summary")

        # Tab 2: Education & Technical Skills
        tab2 = QWidget()
        t2_layout = QVBoxLayout(tab2)
        t2_layout.setContentsMargins(12, 12, 12, 12)
        t2_layout.setSpacing(8)

        t2_layout.addWidget(QLabel("Degree & Major:"))
        h_box3 = QHBoxLayout()
        self.ed_degree = QLineEdit()
        self.ed_degree.textChanged.connect(self._sync_and_preview)
        self.ed_branch = QLineEdit()
        self.ed_branch.textChanged.connect(self._sync_and_preview)
        h_box3.addWidget(self.ed_degree)
        h_box3.addWidget(self.ed_branch)
        t2_layout.addLayout(h_box3)

        t2_layout.addWidget(QLabel("Institution, Graduation Year & CGPA:"))
        h_box4 = QHBoxLayout()
        self.ed_institution = QLineEdit()
        self.ed_institution.textChanged.connect(self._sync_and_preview)
        self.ed_year = QLineEdit()
        self.ed_year.textChanged.connect(self._sync_and_preview)
        self.ed_cgpa = QLineEdit()
        self.ed_cgpa.textChanged.connect(self._sync_and_preview)
        h_box4.addWidget(self.ed_institution)
        h_box4.addWidget(self.ed_year)
        h_box4.addWidget(self.ed_cgpa)
        t2_layout.addLayout(h_box4)

        t2_layout.addWidget(QLabel("Technical Skills - Languages (comma-separated):"))
        self.ed_lang_skills = QLineEdit()
        self.ed_lang_skills.textChanged.connect(self._sync_and_preview)
        t2_layout.addWidget(self.ed_lang_skills)

        t2_layout.addWidget(QLabel("Technical Skills - Frameworks & Libraries:"))
        self.ed_fw_skills = QLineEdit()
        self.ed_fw_skills.textChanged.connect(self._sync_and_preview)
        t2_layout.addWidget(self.ed_fw_skills)

        t2_layout.addWidget(QLabel("Technical Skills - Databases & Tools:"))
        self.ed_tool_skills = QLineEdit()
        self.ed_tool_skills.textChanged.connect(self._sync_and_preview)
        t2_layout.addWidget(self.ed_tool_skills)

        t2_layout.addStretch()
        self.editor_tabs.addTab(tab2, "🎓 Education & Skills")

        # Tab 3: Projects
        tab3 = QWidget()
        t3_layout = QVBoxLayout(tab3)
        t3_layout.setContentsMargins(12, 12, 12, 12)
        t3_layout.setSpacing(8)

        # Project 1
        t3_layout.addWidget(QLabel("<b>Project 1 Title & Role:</b>"))
        h_p1 = QHBoxLayout()
        self.ed_p1_title = QLineEdit()
        self.ed_p1_title.textChanged.connect(self._sync_and_preview)
        self.ed_p1_role = QLineEdit()
        self.ed_p1_role.textChanged.connect(self._sync_and_preview)
        h_p1.addWidget(self.ed_p1_title)
        h_p1.addWidget(self.ed_p1_role)
        t3_layout.addLayout(h_p1)

        t3_layout.addWidget(QLabel("Project 1 Tech Stack & Link:"))
        h_p1_meta = QHBoxLayout()
        self.ed_p1_stack = QLineEdit()
        self.ed_p1_stack.textChanged.connect(self._sync_and_preview)
        self.ed_p1_link = QLineEdit()
        self.ed_p1_link.textChanged.connect(self._sync_and_preview)
        h_p1_meta.addWidget(self.ed_p1_stack)
        h_p1_meta.addWidget(self.ed_p1_link)
        t3_layout.addLayout(h_p1_meta)

        t3_layout.addWidget(QLabel("Project 1 Bullets (one per line):"))
        self.ed_p1_bullets = QTextEdit()
        self.ed_p1_bullets.setMinimumHeight(60)
        self.ed_p1_bullets.textChanged.connect(self._sync_and_preview)
        t3_layout.addWidget(self.ed_p1_bullets)

        # Project 2
        t3_layout.addWidget(QLabel("<b>Project 2 Title & Role:</b>"))
        h_p2 = QHBoxLayout()
        self.ed_p2_title = QLineEdit()
        self.ed_p2_title.textChanged.connect(self._sync_and_preview)
        self.ed_p2_role = QLineEdit()
        self.ed_p2_role.textChanged.connect(self._sync_and_preview)
        h_p2.addWidget(self.ed_p2_title)
        h_p2.addWidget(self.ed_p2_role)
        t3_layout.addLayout(h_p2)

        t3_layout.addWidget(QLabel("Project 2 Tech Stack & Link:"))
        h_p2_meta = QHBoxLayout()
        self.ed_p2_stack = QLineEdit()
        self.ed_p2_stack.textChanged.connect(self._sync_and_preview)
        self.ed_p2_link = QLineEdit()
        self.ed_p2_link.textChanged.connect(self._sync_and_preview)
        h_p2_meta.addWidget(self.ed_p2_stack)
        h_p2_meta.addWidget(self.ed_p2_link)
        t3_layout.addLayout(h_p2_meta)

        t3_layout.addWidget(QLabel("Project 2 Bullets (one per line):"))
        self.ed_p2_bullets = QTextEdit()
        self.ed_p2_bullets.setMinimumHeight(60)
        self.ed_p2_bullets.textChanged.connect(self._sync_and_preview)
        t3_layout.addWidget(self.ed_p2_bullets)

        self.editor_tabs.addTab(tab3, "💻 Projects")

    def load_or_generate_resume(self) -> None:
        self.current_profile = ProfileRepository.get_profile() or StudentProfile()
        target = self.current_profile.career_goal or "Software Developer"
        saved = ResumeRepository.get_resume(target)
        if saved:
            self.current_resume = ResumeData.from_dict(saved)
        else:
            self.current_resume = ResumeBuilder.build_from_profile(self.current_profile, target)
        self._populate_fields_from_resume(self.current_resume)

    def generate_from_current_profile(self) -> None:
        self.current_profile = ProfileRepository.get_profile() or StudentProfile()
        target = self.current_profile.career_goal or "Software Developer"
        self.current_resume = ResumeBuilder.build_from_profile(self.current_profile, target)
        self._populate_fields_from_resume(self.current_resume)
        QMessageBox.information(
            self, "Resume Auto-Generated",
            f"Tailored resume generated for {target} using your profile and skills."
        )

    def set_target_career(self, career_id: str) -> None:
        self.current_profile = ProfileRepository.get_profile() or StudentProfile()
        self.current_resume = ResumeBuilder.build_from_profile(self.current_profile, career_id)
        self._populate_fields_from_resume(self.current_resume)

    def _populate_fields_from_resume(self, resume: ResumeData) -> None:
        self.blockSignals(True)
        # Tab 1
        self.ed_name.setText(resume.contact.name)
        self.ed_email.setText(resume.contact.email)
        self.ed_phone.setText(resume.contact.phone)
        self.ed_loc.setText(resume.contact.location)
        self.ed_linkedin.setText(resume.contact.linkedin)
        self.ed_github.setText(resume.contact.github)
        self.ed_summary.setText(resume.professional_summary)

        # Tab 2
        if resume.education:
            e = resume.education[0]
            self.ed_degree.setText(e.degree)
            self.ed_branch.setText(e.branch)
            self.ed_institution.setText(e.institution)
            self.ed_year.setText(e.year)
            self.ed_cgpa.setText(e.cgpa)

        self.ed_lang_skills.setText(", ".join(resume.technical_skills.get("Programming Languages", [])))
        self.ed_fw_skills.setText(", ".join(resume.technical_skills.get("Frameworks & Libraries", [])))
        self.ed_tool_skills.setText(", ".join(resume.technical_skills.get("Databases & Tools", [])))

        # Tab 3 (Projects)
        if len(resume.projects) >= 1:
            p1 = resume.projects[0]
            self.ed_p1_title.setText(p1.title)
            self.ed_p1_role.setText(p1.role)
            self.ed_p1_stack.setText(p1.tech_stack)
            self.ed_p1_link.setText(p1.github_url)
            self.ed_p1_bullets.setText("\n".join(p1.bullets))
        if len(resume.projects) >= 2:
            p2 = resume.projects[1]
            self.ed_p2_title.setText(p2.title)
            self.ed_p2_role.setText(p2.role)
            self.ed_p2_stack.setText(p2.tech_stack)
            self.ed_p2_link.setText(p2.github_url)
            self.ed_p2_bullets.setText("\n".join(p2.bullets))

        self.blockSignals(False)
        self._sync_and_preview()

    def _sync_and_preview(self) -> None:
        contact = ContactInfo(
            name=self.ed_name.text().strip(),
            email=self.ed_email.text().strip(),
            phone=self.ed_phone.text().strip(),
            location=self.ed_loc.text().strip(),
            linkedin=self.ed_linkedin.text().strip(),
            github=self.ed_github.text().strip()
        )

        edu = EducationEntry(
            degree=self.ed_degree.text().strip(),
            branch=self.ed_branch.text().strip(),
            institution=self.ed_institution.text().strip(),
            year=self.ed_year.text().strip(),
            cgpa=self.ed_cgpa.text().strip()
        )

        skills_map = {}
        langs = parse_comma_separated(self.ed_lang_skills.text())
        if langs:
            skills_map["Programming Languages"] = langs
        fws = parse_comma_separated(self.ed_fw_skills.text())
        if fws:
            skills_map["Frameworks & Libraries"] = fws
        tools = parse_comma_separated(self.ed_tool_skills.text())
        if tools:
            skills_map["Databases & Tools"] = tools

        projects = []
        if self.ed_p1_title.text().strip():
            b1 = [x.strip() for x in self.ed_p1_bullets.toPlainText().split("\n") if x.strip()]
            projects.append(ProjectEntry(
                title=self.ed_p1_title.text().strip(),
                role=self.ed_p1_role.text().strip() or "Developer",
                tech_stack=self.ed_p1_stack.text().strip(),
                github_url=self.ed_p1_link.text().strip(),
                bullets=b1
            ))
        if self.ed_p2_title.text().strip():
            b2 = [x.strip() for x in self.ed_p2_bullets.toPlainText().split("\n") if x.strip()]
            projects.append(ProjectEntry(
                title=self.ed_p2_title.text().strip(),
                role=self.ed_p2_role.text().strip() or "Developer",
                tech_stack=self.ed_p2_stack.text().strip(),
                github_url=self.ed_p2_link.text().strip(),
                bullets=b2
            ))

        target = self.current_profile.career_goal if self.current_profile else "Software Developer"
        self.current_resume = ResumeData(
            target_career=target,
            contact=contact,
            professional_summary=self.ed_summary.toPlainText().strip(),
            education=[edu],
            technical_skills=skills_map,
            projects=projects,
            certifications=self.current_resume.certifications if self.current_resume else [],
            achievements=self.current_resume.achievements if self.current_resume else []
        )

        self.preview_widget.render_resume(self.current_resume, template_id=self.current_template_id)
        self._run_ats_screening()

    def _on_template_changed(self) -> None:
        self.current_template_id = self.template_combo.currentData() or "modern"
        if self.current_resume:
            self.preview_widget.render_resume(self.current_resume, template_id=self.current_template_id)

    def _run_ats_screening(self) -> None:
        if not self.current_resume:
            return
        self.ats_result = LocalATSAnalyzer.analyze(self.current_resume)
        res = self.ats_result
        self.ats_bar.setValue(res.score)
        self.ats_score_badge.setText(f" {res.score} / 100 (Grade: {res.grade}) ")

        color = COLORS.SUCCESS if res.score >= 80 else COLORS.WARNING if res.score >= 60 else COLORS.DANGER
        self.ats_score_badge.setStyleSheet(f"""
            background-color: {COLORS.SUCCESS_BG if res.score >= 80 else COLORS.WARNING_BG};
            color: {color};
            border: 1px solid {color};
            border-radius: 8px;
            padding: 3px 8px;
            font-weight: 800;
            font-size: 12px;
        """)

        # Feedback summary text
        fb = []
        if res.strengths:
            fb.append(f"<b>Key Strengths:</b> {res.strengths[0]}")
        if res.improvements:
            fb.append(f"<b>Suggested Improvement:</b> {res.improvements[0]}")
        self.ats_feedback_lbl.setText("<br>".join(fb))
        self.ats_score_changed.emit(res.score)

    def save_resume(self) -> None:
        if not self.current_resume:
            return
        try:
            target = self.current_resume.target_career or "Software Developer"
            prof_id = self.current_profile.id if self.current_profile else None
            ResumeRepository.save_resume(target, self.current_resume.to_dict(), prof_id)
            QMessageBox.information(self, "Resume Saved", "Resume content saved to local SQLite database.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save resume: {e}")

    def copy_markdown_to_clipboard(self) -> None:
        if not self.current_resume:
            return
        md = ResumeBuilder.export_markdown(self.current_resume)
        clipboard = QApplication.clipboard()
        clipboard.setText(md)
        QMessageBox.information(self, "Copied", "Resume Markdown copied to clipboard!")

    def export_html_file(self) -> None:
        if not self.current_resume:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Resume HTML", str(EXPORTS_DIR / f"resume_{self.current_template_id}.html"), "HTML Files (*.html)"
        )
        if path:
            html_content = ResumeBuilder.export_html(self.current_resume, template_id=self.current_template_id)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_content)
            QMessageBox.information(self, "Export Successful", f"Saved resume HTML to:\n{path}")

    def export_text_file(self) -> None:
        if not self.current_resume:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Plain Text Resume", str(EXPORTS_DIR / "resume.txt"), "Text Files (*.txt)"
        )
        if path:
            txt = ResumeBuilder.export_plain_text(self.current_resume)
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            QMessageBox.information(self, "Export Successful", f"Saved plain text resume to:\n{path}")
