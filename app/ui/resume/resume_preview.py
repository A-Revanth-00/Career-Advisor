from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QFrame
from app.core.config import COLORS
from app.resume.resume_data import ResumeData
from app.resume.resume_builder import ResumeBuilder

class ResumePreviewWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # White page styling for resume paper look
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        layout.addWidget(self.browser)

    def render_resume(self, resume: ResumeData, template_id: str = "modern") -> None:
        html_content = ResumeBuilder.export_html(resume, template_id=template_id)
        self.browser.setHtml(html_content)
