from __future__ import annotations
import os
import sys
from pathlib import Path

# Base project directory
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
APP_DIR: Path = BASE_DIR / "app"
DATA_DIR: Path = BASE_DIR / "data"
TEMPLATES_DIR: Path = DATA_DIR / "templates"
EXPORTS_DIR: Path = BASE_DIR / "exports"

# Data file paths
CAREER_DATABASE_PATH: Path = DATA_DIR / "career_database.json"
LEARNING_RESOURCES_PATH: Path = DATA_DIR / "learning_resources.json"
ROADMAP_TASKS_PATH: Path = DATA_DIR / "roadmap_tasks.json"
RESUME_TEMPLATE_PATH: Path = TEMPLATES_DIR / "resume_template.json"
RESUME_TEMPLATE_MODERN_PATH: Path = TEMPLATES_DIR / "resume_template_modern.json"
RESUME_TEMPLATE_ATS_PATH: Path = TEMPLATES_DIR / "resume_template_ats_safe.json"
RESUME_TEMPLATE_COMPACT_PATH: Path = TEMPLATES_DIR / "resume_template_compact.json"

# SQLite Database Path
DATABASE_PATH: Path = BASE_DIR / "career_advisor.db"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
