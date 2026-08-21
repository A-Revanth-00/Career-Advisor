from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from app.core.paths import CAREER_DATABASE_PATH

logger = logging.getLogger(__name__)

@dataclass
class Career:
    id: str
    name: str
    category: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    useful_interests: List[str] = field(default_factory=list)
    compatible_education: List[str] = field(default_factory=list)
    optional_skills: List[str] = field(default_factory=list)
    market_demand: str = "High"
    salary_range: str = "$75,000 - $130,000"
    responsibilities: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Career":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            category=data.get("category", "General"),
            description=data.get("description", ""),
            required_skills=data.get("required_skills", []),
            useful_interests=data.get("useful_interests", []),
            compatible_education=data.get("compatible_education", []),
            optional_skills=data.get("optional_skills", []),
            market_demand=data.get("market_demand", "High"),
            salary_range=data.get("salary_range", "$75,000 - $130,000"),
            responsibilities=data.get("responsibilities", [])
        )

_CAREER_CACHE: Optional[List[Career]] = None

def load_career_database(force_reload: bool = False) -> List[Career]:
    """Loads all careers from the offline JSON database."""
    global _CAREER_CACHE
    if _CAREER_CACHE is not None and not force_reload:
        return _CAREER_CACHE

    if not CAREER_DATABASE_PATH.exists():
        logger.warning("Career database file not found at %s", CAREER_DATABASE_PATH)
        return []

    try:
        with open(CAREER_DATABASE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            careers_raw = data.get("careers", [])
            _CAREER_CACHE = [Career.from_dict(c) for c in careers_raw]
            return _CAREER_CACHE
    except Exception as e:
        logger.error("Failed to parse career database: %s", e)
        return []

def get_career_by_id(career_id: str) -> Optional[Career]:
    """Finds a specific career by ID."""
    careers = load_career_database()
    for c in careers:
        if c.id == career_id:
            return c
    return None

def get_career_by_name(name: str) -> Optional[Career]:
    """Finds a career by its display name (case-insensitive)."""
    careers = load_career_database()
    target = name.strip().lower()
    for c in careers:
        if c.name.strip().lower() == target:
            return c
    return None

def get_all_careers() -> List[Career]:
    """Returns all available offline careers."""
    return load_career_database()
