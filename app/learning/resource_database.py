from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from app.core.paths import LEARNING_RESOURCES_PATH
from app.core.utils import normalize_skill

logger = logging.getLogger(__name__)

@dataclass
class LearningResource:
    id: str
    title: str
    skill: str
    type: str  # Documentation, Course, Video, Practice, Project
    provider: str
    url: str
    difficulty: str  # Beginner, Intermediate, Advanced
    estimated_hours: int
    description: str
    youtube_url: str = ""

    @classmethod
    def from_dict(cls, d: Dict) -> "LearningResource":
        return cls(
            id=d.get("id", ""),
            title=d.get("title", ""),
            skill=d.get("skill", ""),
            type=d.get("type", "Course"),
            provider=d.get("provider", "General"),
            url=d.get("url", ""),
            difficulty=d.get("difficulty", "Beginner"),
            estimated_hours=int(d.get("estimated_hours", 10)),
            description=d.get("description", ""),
            youtube_url=d.get("youtube_url", "")
        )

_RESOURCE_CACHE: Optional[List[LearningResource]] = None

def load_learning_resources(force_reload: bool = False) -> List[LearningResource]:
    """Loads offline learning resources from JSON database."""
    global _RESOURCE_CACHE
    if _RESOURCE_CACHE is not None and not force_reload:
        return _RESOURCE_CACHE

    if not LEARNING_RESOURCES_PATH.exists():
        logger.warning("Learning resources JSON not found at %s", LEARNING_RESOURCES_PATH)
        return []

    try:
        with open(LEARNING_RESOURCES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            raw = data.get("resources", [])
            _RESOURCE_CACHE = [LearningResource.from_dict(r) for r in raw]
            return _RESOURCE_CACHE
    except Exception as e:
        logger.error("Failed to load learning resources: %s", e)
        return []

def get_resources_by_skill(skill: str) -> List[LearningResource]:
    """Finds resources matching a specific skill name."""
    resources = load_learning_resources()
    target = normalize_skill(skill)
    return [r for r in resources if target in normalize_skill(r.skill) or normalize_skill(r.skill) in target]

def filter_resources(
    skill_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    difficulty_filter: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[LearningResource]:
    """Filters offline resources by skill, content type, difficulty, and keyword search."""
    items = load_learning_resources()
    results = []

    for r in items:
        if skill_filter and skill_filter.lower() != "all":
            if normalize_skill(skill_filter) not in normalize_skill(r.skill):
                continue
        
        if type_filter and type_filter.lower() != "all":
            if r.type.lower() != type_filter.lower():
                continue

        if difficulty_filter and difficulty_filter.lower() != "all":
            if r.difficulty.lower() != difficulty_filter.lower():
                continue

        if search_query:
            q = search_query.lower().strip()
            text_corpus = f"{r.title} {r.skill} {r.provider} {r.description}".lower()
            if q not in text_corpus:
                continue

        results.append(r)

    return results

def get_all_skills_in_resources() -> List[str]:
    """Returns a unique sorted list of skills present in resource database."""
    resources = load_learning_resources()
    skills = sorted({r.skill for r in resources if r.skill})
    return skills
