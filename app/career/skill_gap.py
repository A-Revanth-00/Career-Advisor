from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import List
from app.career.career_data import Career
from app.core.utils import normalize_skill
from app.database.models import StudentProfile

logger = logging.getLogger(__name__)

@dataclass
class SkillGapAnalysis:
    career: Career
    profile: StudentProfile
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    optional_matched: List[str] = field(default_factory=list)
    optional_missing: List[str] = field(default_factory=list)
    skill_readiness: float = 0.0
    interest_alignment: float = 0.0
    education_compatible: bool = False
    education_status: str = ""
    overall_readiness: float = 0.0
    readiness_level: str = "Foundational Gap"
    actionable_steps: List[str] = field(default_factory=list)

class SkillGapAnalyzer:
    @classmethod
    def analyze(cls, profile: StudentProfile, career: Career) -> SkillGapAnalysis:
        """Performs deep, deterministic skill gap analysis against a selected career."""
        student_skills_norm = {normalize_skill(s) for s in profile.skills if s.strip()}
        student_interests_norm = {normalize_skill(i) for i in profile.interests if i.strip()}

        # 1. Match Required Skills
        matched_req = []
        missing_req = []
        for req in career.required_skills:
            req_norm = normalize_skill(req)
            if any(req_norm in s or s in req_norm for s in student_skills_norm):
                matched_req.append(req)
            else:
                missing_req.append(req)

        # 2. Optional skills
        matched_opt = []
        missing_opt = []
        for opt in career.optional_skills:
            opt_norm = normalize_skill(opt)
            if any(opt_norm in s or s in opt_norm for s in student_skills_norm):
                matched_opt.append(opt)
            else:
                missing_opt.append(opt)

        total_req = max(len(career.required_skills), 1)
        skill_readiness = round((len(matched_req) / total_req) * 100.0, 1)

        # 3. Interest alignment
        matched_int = [i for i in career.useful_interests if any(normalize_skill(i) in s or s in normalize_skill(i) for s in student_interests_norm)]
        total_int = max(len(career.useful_interests), 1)
        interest_alignment = round((len(matched_int) / total_int) * 100.0, 1)

        # 4. Education check
        student_branch_norm = profile.branch.lower().strip()
        student_edu_norm = profile.education.lower().strip()
        edu_match = False
        for comp in career.compatible_education:
            comp_norm = comp.lower().strip()
            if (comp_norm in student_branch_norm or student_branch_norm in comp_norm or
                comp_norm in student_edu_norm or student_edu_norm in comp_norm):
                edu_match = True
                break

        edu_score = 100.0 if edu_match else 60.0
        edu_status = "Directly Aligned" if edu_match else "Complementary Background"

        # Overall readiness: 60% skill readiness, 25% interest alignment, 15% education
        overall_readiness = round(
            (skill_readiness * 0.60) +
            (interest_alignment * 0.25) +
            (edu_score * 0.15),
            1
        )
        overall_readiness = min(max(overall_readiness, 0.0), 100.0)

        # Determine readiness level and actionable steps
        if overall_readiness >= 80.0:
            level = "Industry Ready"
            steps = [
                "Build full-scale capstone projects demonstrating end-to-end implementation",
                "Prepare targeted ATS-optimized resume emphasizing production skills",
                "Practice technical interview problem solving and architecture design"
            ]
        elif overall_readiness >= 55.0:
            level = "Near Ready"
            steps = [
                f"Close the core skill gap by mastering: {', '.join(missing_req[:3])}",
                "Develop 2 guided projects applying these missing tools",
                "Deepen conceptual fundamentals through structured exercises"
            ]
        elif overall_readiness >= 30.0:
            level = "Intermediate Gap"
            steps = [
                f"Focus on foundational competencies: {', '.join(missing_req[:4])}",
                "Follow a structured weekly roadmap dedicating regular study hours",
                "Complete hands-on coding drills before attempting complex projects"
            ]
        else:
            level = "Foundational Gap"
            steps = [
                "Establish core programming and computer science building blocks",
                "Work through beginner courses for prerequisite technologies",
                "Build confidence with micro-exercises and code katas"
            ]

        return SkillGapAnalysis(
            career=career,
            profile=profile,
            matched_skills=matched_req,
            missing_skills=missing_req,
            optional_matched=matched_opt,
            optional_missing=missing_opt,
            skill_readiness=skill_readiness,
            interest_alignment=interest_alignment,
            education_compatible=edu_match,
            education_status=edu_status,
            overall_readiness=overall_readiness,
            readiness_level=level,
            actionable_steps=steps
        )
