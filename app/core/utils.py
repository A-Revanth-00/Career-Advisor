from __future__ import annotations
import json
import re
from typing import Any, List, Tuple

# Common skill aliases for intelligent normalization
SKILL_ALIASES = {
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "ts": "typescript",
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "express": "node.js",
    "expressjs": "node.js",
    "c++": "c++",
    "cpp": "c++",
    "postgres": "postgresql",
    "psql": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "dl": "deep learning",
    "dsa": "data structures",
    "algorithms": "algorithms",
    "oop": "object-oriented programming",
    "oops": "object-oriented programming",
    "html": "html5",
    "css": "css3",
    "html/css": "html5 & css3",
    "rest": "rest apis",
    "api": "rest apis",
    "apis": "rest apis",
    "docker": "docker",
    "flutter": "flutter",
    "dart": "dart",
    "powerbi": "power bi",
    "tf": "tensorflow",
    "torch": "pytorch",
    "aws": "aws",
    "git": "git",
    "github": "git",
    "sql": "sql"
}

def normalize_skill(skill: str) -> str:
    """Normalizes skill strings for case-insensitive alias matching."""
    if not skill:
        return ""
    cleaned = skill.strip().lower()
    cleaned = re.sub(r"[\s\-_]+", " ", cleaned)
    return SKILL_ALIASES.get(cleaned, cleaned)

def parse_comma_separated(text: str | None) -> List[str]:
    """Parses a comma or newline separated string into a cleaned list of items."""
    if not text:
        return []
    raw_items = re.split(r"[,;\n]+", str(text))
    items = []
    for item in raw_items:
        val = item.strip()
        if val and val not in items:
            items.append(val)
    return items

def format_list_as_comma(items: List[str] | None) -> str:
    """Formats a list of strings into a clean comma-separated string."""
    if not items:
        return ""
    return ", ".join(str(x).strip() for x in items if str(x).strip())

def safe_json_loads(data: Any, default: Any = None) -> Any:
    """Safely loads JSON string or returns fallback default."""
    if data is None:
        return default if default is not None else []
    if isinstance(data, (list, dict)):
        return data
    try:
        return json.loads(str(data))
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []

def safe_json_dumps(data: Any) -> str:
    """Safely serializes object to JSON string."""
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return "[]"

def validate_cgpa(cgpa_val: Any) -> Tuple[bool, float, str]:
    """Validates CGPA value within reasonable 0.0 - 10.0 range."""
    try:
        cgpa = float(cgpa_val)
        if 0.0 <= cgpa <= 10.0:
            return True, cgpa, "Valid CGPA"
        if 0.0 <= cgpa <= 100.0:
            scaled = round(cgpa / 10.0, 2)
            return True, scaled, f"Scaled percentage to CGPA: {scaled}"
        return False, 0.0, "CGPA must be between 0.0 and 10.0"
    except (ValueError, TypeError):
        return False, 0.0, "Please enter a valid numeric CGPA"

def validate_hours_and_days(hours: Any, days: Any) -> Tuple[bool, float, int, str]:
    """Validates student study hours per day and days per week."""
    try:
        h = float(hours)
        d = int(days)
        if not (0.5 <= h <= 16.0):
            return False, 0.0, 0, "Hours per day should be between 0.5 and 16"
        if not (1 <= d <= 7):
            return False, 0.0, 0, "Days per week must be between 1 and 7"
        return True, h, d, "Valid availability"
    except (ValueError, TypeError):
        return False, 0.0, 0, "Please enter valid numeric values for study time"
