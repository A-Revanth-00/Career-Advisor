from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import List
from app.career.career_data import Career
from app.career.skill_gap import SkillGapAnalyzer
from app.database.models import StudentProfile
from app.learning.resource_database import LearningResource, get_resources_by_skill

logger = logging.getLogger(__name__)

@dataclass
class LearningTrack:
    skill: str
    is_missing: bool
    resources: List[LearningResource] = field(default_factory=list)
    total_hours: int = 0

class LearningPlanner:
    @classmethod
    def generate_curriculum(cls, profile: StudentProfile, career: Career) -> List[LearningTrack]:
        """Generates prioritized learning tracks aligned with student skill gap analysis."""
        gap = SkillGapAnalyzer.analyze(profile, career)
        tracks: List[LearningTrack] = []

        # 1. Missing required skills (highest priority)
        for s in gap.missing_skills:
            res_list = get_resources_by_skill(s)
            if not res_list:
                logger.warning("Skill '%s' not found in learning resources catalog; generating fallback guideline.", s)
                # Create a synthetic offline resource guideline if not in static catalog
                res_list = [
                    LearningResource(
                        id=f"res_{s.lower()}_auto",
                        title=f"{s} Comprehensive Study Guide & Practice",
                        skill=s,
                        type="Documentation",
                        provider="Official Technical Documentation",
                        url=f"https://devdocs.io/",
                        difficulty="Intermediate",
                        estimated_hours=14,
                        description=f"Essential fundamentals, core libraries, and implementation patterns for {s}."
                    )
                ]
            
            tot_h = sum(r.estimated_hours for r in res_list)
            tracks.append(LearningTrack(
                skill=s,
                is_missing=True,
                resources=res_list,
                total_hours=tot_h
            ))

        # 2. Matched skills (refresher / advanced)
        for s in gap.matched_skills[:2]:
            res_list = get_resources_by_skill(s)
            if res_list:
                tot_h = sum(r.estimated_hours for r in res_list)
                tracks.append(LearningTrack(
                    skill=s,
                    is_missing=False,
                    resources=res_list,
                    total_hours=tot_h
                ))

        return tracks
