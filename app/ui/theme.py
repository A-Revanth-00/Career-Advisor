from __future__ import annotations
from app.core.config import COLORS

APP_STYLESHEET = f"""
/* ==========================================================================
   CAREER ADVISOR - Professional Modern Dark Theme
   ========================================================================== */

* {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', 'Roboto', Arial, sans-serif;
    color: {COLORS.TEXT_MAIN};
    outline: none;
}}

QMainWindow, QWidget#centralWidget {{
    background-color: {COLORS.BG_DARK};
}}

/* Sidebar */
QWidget#sidebar {{
    background-color: {COLORS.BG_SIDEBAR};
    border-right: 1px solid {COLORS.BORDER};
}}

QLabel#brandTitle {{
    font-size: 19px;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: {COLORS.PRIMARY_LIGHT};
}}

QLabel#brandSubtitle {{
    font-size: 11px;
    font-weight: 500;
    color: {COLORS.TEXT_MUTED};
    letter-spacing: 0.5px;
}}

/* Navigation Buttons */
QPushButton.nav-btn {{
    text-align: left;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 8px;
    border: 1px solid transparent;
    background-color: transparent;
    color: {COLORS.TEXT_MUTED};
    margin: 2px 8px;
}}

QPushButton.nav-btn:hover {{
    background-color: {COLORS.BG_CARD};
    color: {COLORS.TEXT_MAIN};
}}

QPushButton.nav-btn:checked {{
    background-color: {COLORS.PRIMARY_MUTED};
    color: {COLORS.PRIMARY_LIGHT};
    border: 1px solid rgba(59, 130, 246, 0.4);
}}

/* Header Bar */
QWidget#headerBar {{
    background-color: {COLORS.BG_HEADER};
    border-bottom: 1px solid {COLORS.BORDER};
    padding: 8px 24px;
}}

QLabel#pageTitle {{
    font-size: 20px;
    font-weight: 700;
    color: {COLORS.TEXT_MAIN};
}}

QLabel#pageSubtitle {{
    font-size: 12px;
    color: {COLORS.TEXT_MUTED};
}}

/* Cards */
QFrame.card {{
    background-color: {COLORS.BG_CARD};
    border: 1px solid {COLORS.BORDER};
    border-radius: 12px;
    padding: 16px;
}}

QFrame.card:hover {{
    border: 1px solid {COLORS.BORDER_LIGHT};
}}

QFrame.card-highlight {{
    background-color: {COLORS.BG_CARD};
    border: 1px solid {COLORS.PRIMARY};
    border-radius: 12px;
    padding: 16px;
}}

/* Typography */
QLabel.card-title {{
    font-size: 16px;
    font-weight: 700;
    color: {COLORS.TEXT_MAIN};
}}

QLabel.card-subtitle {{
    font-size: 12px;
    color: {COLORS.TEXT_MUTED};
}}

QLabel.metric-value {{
    font-size: 28px;
    font-weight: 800;
    color: {COLORS.PRIMARY_LIGHT};
}}

QLabel.metric-label {{
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: {COLORS.TEXT_MUTED};
}}

/* Inputs & Form Controls */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {COLORS.BG_INPUT};
    border: 1px solid {COLORS.BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {COLORS.TEXT_MAIN};
    selection-background-color: {COLORS.PRIMARY};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {COLORS.PRIMARY};
    background-color: #0d1629;
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS.BG_CARD};
    border: 1px solid {COLORS.BORDER};
    selection-background-color: {COLORS.PRIMARY};
    selection-color: #ffffff;
    padding: 4px;
}}

/* Buttons */
QPushButton.btn-primary {{
    background-color: {COLORS.PRIMARY};
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 8px;
    padding: 9px 18px;
    border: none;
}}

QPushButton.btn-primary:hover {{
    background-color: {COLORS.PRIMARY_HOVER};
}}

QPushButton.btn-primary:pressed {{
    background-color: #1d4ed8;
}}

QPushButton.btn-secondary {{
    background-color: transparent;
    color: {COLORS.TEXT_MAIN};
    font-weight: 600;
    font-size: 13px;
    border-radius: 8px;
    padding: 8px 16px;
    border: 1px solid {COLORS.BORDER_LIGHT};
}}

QPushButton.btn-secondary:hover {{
    background-color: {COLORS.BG_CARD_HOVER};
    border-color: {COLORS.PRIMARY_LIGHT};
}}

QPushButton.btn-success {{
    background-color: {COLORS.SUCCESS};
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 8px;
    padding: 9px 18px;
    border: none;
}}

QPushButton.btn-success:hover {{
    background-color: #059669;
}}

QPushButton.chip-btn {{
    background-color: rgba(59, 130, 246, 0.1);
    color: {COLORS.PRIMARY_LIGHT};
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 14px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}}

QPushButton.chip-btn:hover {{
    background-color: {COLORS.PRIMARY};
    color: #ffffff;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS.BG_INPUT};
    border: 1px solid {COLORS.BORDER};
    border-radius: 6px;
    text-align: center;
    font-size: 11px;
    font-weight: 700;
    color: {COLORS.TEXT_MAIN};
    min-height: 14px;
    max-height: 14px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS.PRIMARY}, stop:1 {COLORS.SUCCESS});
    border-radius: 5px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {COLORS.BG_DARK};
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS.BORDER};
    min-height: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS.BORDER_LIGHT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {COLORS.BG_DARK};
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS.BORDER};
    min-width: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS.BORDER_LIGHT};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Checkboxes */
QCheckBox {{
    font-size: 13px;
    color: {COLORS.TEXT_MAIN};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {COLORS.BORDER_LIGHT};
    background-color: {COLORS.BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS.SUCCESS};
    border: 1px solid {COLORS.SUCCESS};
}}

/* Tabs */
QTabWidget::pane {{
    border: 1px solid {COLORS.BORDER};
    border-radius: 8px;
    background-color: {COLORS.BG_CARD};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {COLORS.BG_INPUT};
    color: {COLORS.TEXT_MUTED};
    border: 1px solid {COLORS.BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
    font-weight: 600;
    font-size: 12px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS.BG_CARD};
    color: {COLORS.PRIMARY_LIGHT};
    border-top: 2px solid {COLORS.PRIMARY};
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS.BG_CARD_HOVER};
    color: {COLORS.TEXT_MAIN};
}}
"""
