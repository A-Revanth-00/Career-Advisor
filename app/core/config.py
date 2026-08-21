from __future__ import annotations
from dataclasses import dataclass

APP_NAME: str = "CAREER ADVISOR"
APP_TAGLINE: str = "Offline Career Planning & Readiness Studio for Students"
APP_VERSION: str = "1.0.0"
OFFLINE_MODE: bool = True

# Match scoring weights (Deterministic)
WEIGHT_SKILLS: float = 0.50
WEIGHT_INTERESTS: float = 0.35
WEIGHT_EDUCATION: float = 0.15

# UI Color Palette (Professional Dark Theme)
@dataclass(frozen=True)
class ThemeColors:
    BG_DARK: str = "#0f172a"          # Slate 900
    BG_SIDEBAR: str = "#0b1120"       # Deep Slate
    BG_CARD: str = "#1e293b"          # Slate 800
    BG_CARD_HOVER: str = "#283548"    # Slate 750
    BG_INPUT: str = "#0b1324"         # Slate 950
    BG_HEADER: str = "#131c31"        # Header Dark
    
    PRIMARY: str = "#3b82f6"          # Blue 500
    PRIMARY_HOVER: str = "#2563eb"    # Blue 600
    PRIMARY_LIGHT: str = "#60a5fa"    # Blue 400
    PRIMARY_MUTED: str = "rgba(59, 130, 246, 0.15)"
    
    ACCENT: str = "#8b5cf6"           # Violet 500
    ACCENT_LIGHT: str = "#a78bfa"     # Violet 400
    
    SUCCESS: str = "#10b981"          # Emerald 500
    SUCCESS_BG: str = "rgba(16, 185, 129, 0.15)"
    
    WARNING: str = "#f59e0b"          # Amber 500
    WARNING_BG: str = "rgba(245, 158, 11, 0.15)"
    
    DANGER: str = "#ef4444"           # Red 500
    DANGER_BG: str = "rgba(239, 68, 68, 0.15)"
    
    TEXT_MAIN: str = "#f8fafc"        # Slate 50
    TEXT_MUTED: str = "#94a3b8"       # Slate 400
    TEXT_SUBTLE: str = "#64748b"      # Slate 500
    
    BORDER: str = "#334155"           # Slate 700
    BORDER_LIGHT: str = "#475569"     # Slate 600
    BORDER_FOCUS: str = "#3b82f6"     # Blue 500

COLORS = ThemeColors()
