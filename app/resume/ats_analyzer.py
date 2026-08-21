from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Set
from app.career.career_data import get_career_by_id, get_career_by_name
from app.core.utils import normalize_skill
from app.resume.resume_data import ResumeData

@dataclass
class ATSAnalysisResult:
    score: int
    grade: str
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    matched_keywords: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    metrics_detected: int = 0
    action_verbs_count: int = 0

class LocalATSAnalyzer:
    ACTION_VERBS = {
        "developed", "built", "engineered", "designed", "architected",
        "implemented", "optimized", "created", "integrated", "managed",
        "deployed", "analyzed", "automated", "streamlined", "configured",
        "maintained", "trained", "collaborated", "spearheaded", "accelerated",
        "reduced", "increased", "delivered", "scaled", "formulated"
    }

    @classmethod
    def analyze(cls, resume: ResumeData) -> ATSAnalysisResult:
        """Performs comprehensive local heuristic ATS screening."""
        score = 100
        strengths: List[str] = []
        improvements: List[str] = []

        # 1. Contact Information Check
        c = resume.contact
        contact_penalties = 0
        if not c.name or len(c.name.strip()) < 2:
            contact_penalties += 15
            improvements.append("Full candidate name is missing or incomplete.")
        if not c.email or "@" not in c.email:
            contact_penalties += 10
            improvements.append("Valid professional email address is missing.")
        if not c.phone or len(c.phone.strip()) < 7:
            contact_penalties += 5
            improvements.append("Contact phone number is missing.")
        if not c.github and not c.linkedin:
            contact_penalties += 5
            improvements.append("Include at least one GitHub or LinkedIn profile link.")

        if contact_penalties == 0:
            strengths.append("Complete, ATS-readable contact details (Name, Email, Phone, Socials).")
        score -= contact_penalties

        # 2. Target Career & Skill Keyword Matching
        target = resume.target_career or "Software Developer"
        career = get_career_by_id(target) or get_career_by_name(target)
        
        # Flatten all resume text to check keywords
        all_text = f"{resume.professional_summary} {resume.career_objective} ".lower()
        for cat, slist in resume.technical_skills.items():
            all_text += " ".join(slist).lower() + " "
        for p in resume.projects:
            all_text += f"{p.title} {p.tech_stack} {' '.join(p.bullets)} ".lower()

        matched_kw: List[str] = []
        missing_kw: List[str] = []

        if career and career.required_skills:
            for req in career.required_skills:
                req_norm = normalize_skill(req)
                if req_norm in all_text or req.lower() in all_text:
                    matched_kw.append(req)
                else:
                    missing_kw.append(req)

            keyword_ratio = len(matched_kw) / max(len(career.required_skills), 1)
            if keyword_ratio >= 0.7:
                strengths.append(f"Strong keyword density for {career.name} ({len(matched_kw)}/{len(career.required_skills)} core skills).")
            elif keyword_ratio >= 0.4:
                penalty = 10
                score -= penalty
                improvements.append(f"Incorporate missing core {career.name} keywords: {', '.join(missing_kw[:3])}.")
            else:
                penalty = 20
                score -= penalty
                improvements.append(f"Low match for {career.name} target profile. Add key technologies: {', '.join(missing_kw[:4])}.")
        else:
            strengths.append("Technical skills section provided.")

        # 3. Summary Length & Quality Check
        words = resume.professional_summary.strip().split()
        word_count = len(words)
        if word_count == 0:
            score -= 10
            improvements.append("Add a concise professional summary (40-70 words) highlighting strengths.")
        elif word_count < 25:
            score -= 5
            improvements.append("Professional summary is too brief. Expand on technical background.")
        elif word_count > 120:
            score -= 5
            improvements.append("Professional summary is overly verbose. Keep under 80 words for recruiter readability.")
        else:
            strengths.append(f"Well-proportioned professional summary ({word_count} words).")

        # 4. Project Quality: Action Verbs & Quantifiable Metrics
        all_bullet_text = ""
        action_verbs_found: Set[str] = set()
        metrics_found = 0

        for p in resume.projects:
            for b in p.bullets:
                all_bullet_text += b + " "
                # Check action verbs
                b_words = re.findall(r"\b[a-zA-Z]+\b", b.lower())
                if b_words:
                    first_word = b_words[0]
                    if first_word in cls.ACTION_VERBS:
                        action_verbs_found.add(first_word)
                    for w in b_words[:3]:
                        if w in cls.ACTION_VERBS:
                            action_verbs_found.add(w)

                # Check numbers, percentages, speedups
                if re.search(r"(\d+%|\d+\+|\d+x|\b\d+\b|reduced|slashed|accelerated)", b, re.IGNORECASE):
                    metrics_found += 1

        if len(resume.projects) == 0:
            score -= 20
            improvements.append("Add at least 2 technical projects demonstrating hands-on expertise.")
        else:
            if len(action_verbs_found) >= 3:
                strengths.append(f"Strong action-oriented bullet points ({len(action_verbs_found)} distinct action verbs).")
            else:
                score -= 8
                improvements.append("Begin project bullet points with strong power verbs (e.g., Developed, Engineered, Optimized).")

            if metrics_found >= 2:
                strengths.append(f"Quantifiable achievements detected ({metrics_found} impact metrics/percentages).")
            else:
                score -= 7
                improvements.append("Add measurable outcomes to project bullets (e.g., 'reduced latency by 35%', 'processed 500+ requests').")

        # 5. Section Completeness Check
        if not resume.education:
            score -= 10
            improvements.append("Education section is missing.")
        else:
            strengths.append("Education background and GPA clearly formatted.")

        final_score = max(min(score, 100), 20)

        if final_score >= 88:
            grade = "A+"
        elif final_score >= 78:
            grade = "A"
        elif final_score >= 65:
            grade = "B"
        elif final_score >= 50:
            grade = "C"
        else:
            grade = "D"

        return ATSAnalysisResult(
            score=final_score,
            grade=grade,
            strengths=strengths,
            improvements=improvements,
            matched_keywords=matched_kw,
            missing_keywords=missing_kw,
            metrics_detected=metrics_found,
            action_verbs_count=len(action_verbs_found)
        )
