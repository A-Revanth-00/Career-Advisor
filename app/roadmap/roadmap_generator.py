from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from app.career.career_data import Career, get_career_by_id
from app.career.skill_gap import SkillGapAnalyzer
from app.core.paths import ROADMAP_TASKS_PATH
from app.core.utils import normalize_skill
from app.database.models import StudentProfile

logger = logging.getLogger(__name__)

@dataclass
class RoadmapTask:
    id: str
    phase_num: int
    phase_title: str
    title: str
    description: str
    category: str
    skill: str
    estimated_hours: float
    priority: str = "High"  # High, Medium, Low
    is_missing_skill: bool = True
    suggested_resources: List[str] = field(default_factory=list)

@dataclass
class Roadmap:
    career_id: str
    career_name: str
    tasks: List[RoadmapTask] = field(default_factory=list)
    total_hours: float = 0.0

    @property
    def phase_1_tasks(self) -> List[RoadmapTask]:
        return [t for t in self.tasks if t.phase_num == 1]

    @property
    def phase_2_tasks(self) -> List[RoadmapTask]:
        return [t for t in self.tasks if t.phase_num == 2]

    @property
    def phase_3_tasks(self) -> List[RoadmapTask]:
        return [t for t in self.tasks if t.phase_num == 3]

    @property
    def phase_4_tasks(self) -> List[RoadmapTask]:
        return [t for t in self.tasks if t.phase_num == 4]

_ROADMAP_LIBRARY_CACHE: Optional[Dict] = None

def load_roadmap_tasks_library(force_reload: bool = False) -> Dict:
    """Loads curated roadmap task templates and career projects from offline JSON."""
    global _ROADMAP_LIBRARY_CACHE
    if _ROADMAP_LIBRARY_CACHE is not None and not force_reload:
        return _ROADMAP_LIBRARY_CACHE

    if not ROADMAP_TASKS_PATH.exists():
        logger.warning("Roadmap tasks JSON file not found at %s", ROADMAP_TASKS_PATH)
        return {"tasks_by_skill": {}, "career_projects": {}}

    try:
        with open(ROADMAP_TASKS_PATH, "r", encoding="utf-8") as f:
            _ROADMAP_LIBRARY_CACHE = json.load(f)
            return _ROADMAP_LIBRARY_CACHE
    except Exception as e:
        logger.error("Failed to load roadmap tasks library: %s", e)
        return {"tasks_by_skill": {}, "career_projects": {}}

def get_task_template_for_skill(skill: str) -> Optional[Dict]:
    """Finds curated task template for a skill."""
    lib = load_roadmap_tasks_library()
    tasks_map = lib.get("tasks_by_skill", {})
    if skill in tasks_map:
        return tasks_map[skill]
    
    target = normalize_skill(skill)
    for k, v in tasks_map.items():
        if normalize_skill(k) == target:
            return v
    return None

class RoadmapGenerator:
    @classmethod
    def generate(cls, profile: StudentProfile, career: Career) -> Roadmap:
        """Generates a personalized, 4-phase structured roadmap tailored to student skill gaps."""
        gap_analysis = SkillGapAnalyzer.analyze(profile, career)
        missing_skills = gap_analysis.missing_skills
        matched_skills = gap_analysis.matched_skills

        tasks: List[RoadmapTask] = []
        task_counter = 1

        # -------------------------------------------------------------
        # PHASE 1: Foundation (Prerequisites, Core Languages & Systems)
        # -------------------------------------------------------------
        phase_1_title = "Phase 1: Foundation"
        foundational_skills = [
            s for s in missing_skills
            if s in ["Python", "JavaScript", "TypeScript", "SQL", "Git", "Mathematics & Statistics", "Mathematics & Linear Algebra", "Linux", "Data Structures", "Algorithms", "C", "C++", "HTML5 & CSS3", "Bash", "Hardware & OS"]
        ]
        if not foundational_skills and missing_skills:
            foundational_skills = missing_skills[:2]

        for s in foundational_skills:
            tpl = get_task_template_for_skill(s)
            if tpl:
                task_title = tpl.get("title", f"Master Fundamentals of {s}")
                task_desc = tpl.get("description", f"Study syntax, foundational paradigms, core data types, standard libraries, and key concepts for {s}.")
                category = tpl.get("category", "Foundation")
                hours = float(tpl.get("estimated_hours", 10.0))
                priority = tpl.get("priority", "High")
                resources = tpl.get("suggested_resources", [f"{s} Official Documentation", f"Interactive {s} Practice Drills"])
            else:
                logger.warning("No roadmap task template found for skill '%s' (Phase 1), using fallback f-string generator.", s)
                hours = 12.0 if s in ["Data Structures", "Algorithms", "Mathematics & Statistics"] else 8.0
                task_title = f"Master Fundamentals of {s}"
                task_desc = f"Study syntax, foundational paradigms, core data types, standard libraries, and key concepts for {s}."
                category = "Foundation"
                priority = "High"
                resources = [f"{s} Official Documentation", f"Interactive {s} Practice Drills"]

            tasks.append(RoadmapTask(
                id=f"task_{task_counter}",
                phase_num=1,
                phase_title=phase_1_title,
                title=task_title,
                description=task_desc,
                category=category,
                skill=s,
                estimated_hours=hours,
                priority=priority,
                is_missing_skill=True,
                suggested_resources=resources
            ))
            task_counter += 1

        # Always include version control & code hygiene if missing
        if "Git" in missing_skills and "Git" not in foundational_skills:
            tpl = get_task_template_for_skill("Git")
            if tpl:
                task_title = tpl.get("title", "Version Control with Git & GitHub")
                task_desc = tpl.get("description", "Master branching, pull requests, merge conflict resolution, and collaborative Git workflows.")
                category = tpl.get("category", "Tooling")
                hours = float(tpl.get("estimated_hours", 6.0))
                priority = tpl.get("priority", "High")
                resources = tpl.get("suggested_resources", ["Pro Git Book", "GitHub Skills Interactive Labs"])
            else:
                logger.warning("No roadmap task template found for skill 'Git' (Phase 1), using fallback f-string generator.")
                task_title = "Version Control with Git & GitHub"
                task_desc = "Master branching, pull requests, merge conflict resolution, and collaborative Git workflows."
                category = "Tooling"
                hours = 6.0
                priority = "High"
                resources = ["Pro Git Book", "GitHub Skills Interactive Labs"]

            tasks.append(RoadmapTask(
                id=f"task_{task_counter}",
                phase_num=1,
                phase_title=phase_1_title,
                title=task_title,
                description=task_desc,
                category=category,
                skill="Git",
                estimated_hours=hours,
                priority=priority,
                is_missing_skill=True,
                suggested_resources=resources
            ))
            task_counter += 1

        # -------------------------------------------------------------
        # PHASE 2: Core Skills (Specialized Frameworks & Domain Tools)
        # -------------------------------------------------------------
        phase_2_title = "Phase 2: Core Skills"
        core_missing = [s for s in missing_skills if s not in foundational_skills and s != "Git"]
        
        for s in core_missing:
            tpl = get_task_template_for_skill(s)
            if tpl:
                task_title = tpl.get("title", f"Deep Dive into {s}")
                task_desc = tpl.get("description", f"Learn production-grade architecture, design patterns, testing, and ecosystem libraries for {s}.")
                category = tpl.get("category", "Core Technology")
                hours = float(tpl.get("estimated_hours", 14.0))
                priority = tpl.get("priority", "High")
                resources = tpl.get("suggested_resources", [f"Hands-on {s} Masterclass", f"{s} Guided Exercises"])
            else:
                logger.warning("No roadmap task template found for skill '%s' (Phase 2), using fallback f-string generator.", s)
                task_title = f"Deep Dive into {s}"
                task_desc = f"Learn production-grade architecture, design patterns, testing, and ecosystem libraries for {s}."
                category = "Core Technology"
                hours = 14.0
                priority = "High"
                resources = [f"Hands-on {s} Masterclass", f"{s} Guided Exercises"]

            tasks.append(RoadmapTask(
                id=f"task_{task_counter}",
                phase_num=2,
                phase_title=phase_2_title,
                title=task_title,
                description=task_desc,
                category=category,
                skill=s,
                estimated_hours=hours,
                priority=priority,
                is_missing_skill=True,
                suggested_resources=resources
            ))
            task_counter += 1

        # Also add a refresher/advanced task for already matched core skills
        if matched_skills:
            lead_matched = matched_skills[0]
            tpl = get_task_template_for_skill(lead_matched)
            if tpl:
                task_title = f"Advanced Mastery & Architecture: {lead_matched}"
                task_desc = f"Elevate your proficiency in {lead_matched} with enterprise design patterns, performance tuning, and scalable architecture."
                category = "Skill Enhancement"
                hours = 8.0
                priority = "Medium"
                resources = [f"Advanced {lead_matched} Architecture Guide"]
            else:
                logger.warning("No roadmap task template found for matched skill '%s', using fallback.", lead_matched)
                task_title = f"Advanced Concepts in {lead_matched}"
                task_desc = f"Elevate your existing proficiency in {lead_matched} with performance optimization and enterprise patterns."
                category = "Skill Enhancement"
                hours = 8.0
                priority = "Medium"
                resources = [f"Advanced {lead_matched} Architecture"]

            tasks.append(RoadmapTask(
                id=f"task_{task_counter}",
                phase_num=2,
                phase_title=phase_2_title,
                title=task_title,
                description=task_desc,
                category=category,
                skill=lead_matched,
                estimated_hours=hours,
                priority=priority,
                is_missing_skill=False,
                suggested_resources=resources
            ))
            task_counter += 1

        # -------------------------------------------------------------
        # PHASE 3: Projects (Hands-on Portfolio Capstones)
        # -------------------------------------------------------------
        phase_3_title = "Phase 3: Projects"
        project_templates = cls._get_career_projects(career.id, career.name)
        for proj in project_templates:
            tasks.append(RoadmapTask(
                id=f"task_{task_counter}",
                phase_num=3,
                phase_title=phase_3_title,
                title=proj["title"],
                description=proj["description"],
                category="Portfolio Project",
                skill=proj["skill"],
                estimated_hours=proj["hours"],
                priority=proj.get("priority", "High"),
                is_missing_skill=False,
                suggested_resources=["GitHub Repo Boilerplate", "Architecture Specification Guide"]
            ))
            task_counter += 1

        # -------------------------------------------------------------
        # PHASE 4: Career Preparation (Resume, Portfolio & Interviews)
        # -------------------------------------------------------------
        phase_4_title = "Phase 4: Career Preparation"
        tasks.append(RoadmapTask(
            id=f"task_{task_counter}",
            phase_num=4,
            phase_title=phase_4_title,
            title=f"Resume Optimization for {career.name}",
            description="Tailor technical summary, project metrics, and skill sections using ATS-compliant formatting.",
            category="Career Prep",
            skill="Resume Studio",
            estimated_hours=5.0,
            priority="High",
            is_missing_skill=False,
            suggested_resources=["Career Advisor Resume Studio & ATS Analyzer"]
        ))
        task_counter += 1

        tasks.append(RoadmapTask(
            id=f"task_{task_counter}",
            phase_num=4,
            phase_title=phase_4_title,
            title=f"{career.name} Technical Interview Prep",
            description="Review core algorithmic challenges, domain-specific design questions, and mock interview scenarios.",
            category="Interview Prep",
            skill="Technical Interviews",
            estimated_hours=12.0,
            priority="High",
            is_missing_skill=False,
            suggested_resources=["NeetCode Coding Patterns", "System Design Primer"]
        ))
        task_counter += 1

        total_hours = sum(t.estimated_hours for t in tasks)
        return Roadmap(
            career_id=career.id,
            career_name=career.name,
            tasks=tasks,
            total_hours=total_hours
        )

    @classmethod
    def _get_career_projects(cls, career_id: str, career_name: str) -> List[Dict]:
        """Provides tailored real-world project assignments for each career path."""
        lib = load_roadmap_tasks_library()
        projects_map = lib.get("career_projects", {})
        if career_id in projects_map:
            return projects_map[career_id]

        logger.warning("No curated Phase 3 project templates found for career_id '%s', using generic fallback.", career_id)
        return [
            {
                "title": f"Production-Ready {career_name} Portfolio Project",
                "description": f"Design, build, test, and document a comprehensive real-world application showcasing core {career_name} skills.",
                "skill": career_name,
                "hours": 18.0,
                "priority": "High"
            },
            {
                "title": "Open Source Contribution or Case Study Solution",
                "description": "Solve a practical industry problem with clean architecture, CI/CD pipeline, and public GitHub repository.",
                "skill": "System Design",
                "hours": 14.0,
                "priority": "Medium"
            }
        ]
