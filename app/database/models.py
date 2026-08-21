from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.utils import safe_json_loads, safe_json_dumps, format_list_as_comma, parse_comma_separated

@dataclass
class StudentProfile:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    education: str = "B.Tech"
    branch: str = "Computer Science"
    cgpa: float = 8.0
    skills: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    career_goal: str = "Software Developer"
    hours_per_day: float = 2.0
    days_per_week: int = 5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def weekly_hours(self) -> float:
        return round(self.hours_per_day * self.days_per_week, 1)

    @property
    def skills_csv(self) -> str:
        return format_list_as_comma(self.skills)

    @property
    def interests_csv(self) -> str:
        return format_list_as_comma(self.interests)

    @property
    def is_complete(self) -> bool:
        return bool(self.name.strip() and self.email.strip() and self.skills and self.career_goal.strip())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "education": self.education,
            "branch": self.branch,
            "cgpa": self.cgpa,
            "skills": safe_json_dumps(self.skills),
            "interests": safe_json_dumps(self.interests),
            "career_goal": self.career_goal,
            "hours_per_day": self.hours_per_day,
            "days_per_week": self.days_per_week,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row: Any) -> "StudentProfile":
        if not row:
            return cls()
        if hasattr(row, "keys"):
            d = dict(row)
            skills_raw = d.get("skills", "[]")
            interests_raw = d.get("interests", "[]")
            
            if isinstance(skills_raw, str) and (skills_raw.startswith("[") and skills_raw.endswith("]")):
                skills = safe_json_loads(skills_raw, [])
            else:
                skills = parse_comma_separated(skills_raw)

            if isinstance(interests_raw, str) and (interests_raw.startswith("[") and interests_raw.endswith("]")):
                interests = safe_json_loads(interests_raw, [])
            else:
                interests = parse_comma_separated(interests_raw)

            return cls(
                id=d.get("id"),
                name=d.get("name", "") or "",
                email=d.get("email", "") or "",
                education=d.get("education", "B.Tech") or "B.Tech",
                branch=d.get("branch", "Computer Science") or "Computer Science",
                cgpa=float(d.get("cgpa", 8.0) or 8.0),
                skills=skills,
                interests=interests,
                career_goal=d.get("career_goal", "Software Developer") or "Software Developer",
                hours_per_day=float(d.get("hours_per_day", 2.0) or 2.0),
                days_per_week=int(d.get("days_per_week", 5) or 5),
                created_at=d.get("created_at", "") or datetime.now().isoformat(),
                updated_at=d.get("updated_at", "") or datetime.now().isoformat(),
            )
        return cls()

@dataclass
class RoadmapTaskProgress:
    id: Optional[int] = None
    career_id: str = ""
    task_id: str = ""
    completed: bool = False
    completed_at: Optional[str] = None
    notes: str = ""
