from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import List, Tuple
from app.career.career_data import Career, load_career_database
from app.core.config import WEIGHT_SKILLS, WEIGHT_INTERESTS, WEIGHT_EDUCATION
from app.core.utils import normalize_skill
from app.database.models import StudentProfile

logger = logging.getLogger(__name__)

@dataclass
class CareerMatchResult:
    career: Career
    score: float
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    matched_interests: List[str] = field(default_factory=list)
    missing_interests: List[str] = field(default_factory=list)
    education_match: bool = False
    education_score: float = 0.0
    skill_score: float = 0.0
    interest_score: float = 0.0
    match_level: str = "Developing Match"
    recommendation_summary: str = ""

    @property
    def career_id(self) -> str:
        return self.career.id

    @property
    def career_name(self) -> str:
        return self.career.name

    @property
    def category(self) -> str:
        return self.career.category

    @property
    def description(self) -> str:
        return self.career.description

class CareerMatcher:
    @classmethod
    def calculate_match(cls, profile: StudentProfile, career: Career) -> CareerMatchResult:
        """Calculates deterministic transparent profile match score for a career."""
        student_skills_norm = {normalize_skill(s) for s in profile.skills if s.strip()}
        student_interests_norm = {normalize_skill(i) for i in profile.interests if i.strip()}
        
        # 1. Match Required Skills
        matched_req = []
        missing_req = []
        for req in career.required_skills:
            req_norm = normalize_skill(req)
            # Check direct or substring match
            found = any(req_norm in s or s in req_norm for s in student_skills_norm)
            if found:
                matched_req.append(req)
            else:
                missing_req.append(req)

        # Optional skills bonus
        matched_opt = []
        for opt in career.optional_skills:
            opt_norm = normalize_skill(opt)
            if any(opt_norm in s or s in opt_norm for s in student_skills_norm):
                matched_opt.append(opt)

        total_req_count = max(len(career.required_skills), 1)
        base_skill_ratio = len(matched_req) / total_req_count
        opt_bonus = min(len(matched_opt) * 0.05, 0.15)
        skill_score = min((base_skill_ratio + opt_bonus) * 100.0, 100.0)

        # 2. Match Interests
        matched_int = []
        missing_int = []
        total_int_count = max(len(career.useful_interests), 1)
        for interest in career.useful_interests:
            int_norm = normalize_skill(interest)
            found = any(int_norm in i or i in int_norm for i in student_interests_norm)
            if found:
                matched_int.append(interest)
            else:
                missing_int.append(interest)
        
        interest_score = min((len(matched_int) / total_int_count) * 100.0, 100.0)

        # 3. Match Education / Branch
        edu_score = 50.0  # baseline for any formal education
        edu_matched = False
        student_branch_norm = profile.branch.lower().strip()
        student_edu_norm = profile.education.lower().strip()

        for comp in career.compatible_education:
            comp_norm = comp.lower().strip()
            if (comp_norm in student_branch_norm or student_branch_norm in comp_norm or
                comp_norm in student_edu_norm or student_edu_norm in comp_norm):
                edu_matched = True
                edu_score = 100.0
                break

        # Weighting Formula
        final_score = (
            (skill_score * WEIGHT_SKILLS) +
            (interest_score * WEIGHT_INTERESTS) +
            (edu_score * WEIGHT_EDUCATION)
        )
        final_score = round(min(max(final_score, 0.0), 100.0), 1)

        # Match level descriptor
        if final_score >= 75.0:
            level = "Strong Match"
            summary = f"High alignment with your skills and background ({len(matched_req)}/{len(career.required_skills)} core skills)."
        elif final_score >= 45.0:
            level = "Moderate Match"
            summary = f"Good baseline. Building {len(missing_req)} key skills will significantly elevate readiness."
        else:
            level = "Developing Match"
            summary = f"Emerging pathway. Requires focused foundational training across {len(missing_req)} core skills."

        return CareerMatchResult(
            career=career,
            score=final_score,
            matched_skills=matched_req,
            missing_skills=missing_req,
            matched_interests=matched_int,
            missing_interests=missing_int,
            education_match=edu_matched,
            education_score=edu_score,
            skill_score=round(skill_score, 1),
            interest_score=round(interest_score, 1),
            match_level=level,
            recommendation_summary=summary
        )

    @classmethod
    def rank_careers(cls, profile: StudentProfile) -> List[CareerMatchResult]:
        """Ranks all careers in descending order of profile match score."""
        careers = load_career_database()
        results = [cls.calculate_match(profile, c) for c in careers]
        results.sort(key=lambda x: x.score, reverse=True)
        return results
