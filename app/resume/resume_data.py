from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.core.utils import safe_json_loads, safe_json_dumps

@dataclass
class ContactInfo:
    name: str = ""
    email: str = ""
    phone: str = "+1 (555) 019-2834"
    location: str = "City, State / Remote"
    linkedin: str = "linkedin.com/in/studentprofile"
    github: str = "github.com/studentprofile"
    portfolio: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
            "github": self.github,
            "portfolio": self.portfolio
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "ContactInfo":
        return cls(
            name=d.get("name", ""),
            email=d.get("email", ""),
            phone=d.get("phone", ""),
            location=d.get("location", ""),
            linkedin=d.get("linkedin", ""),
            github=d.get("github", ""),
            portfolio=d.get("portfolio", "")
        )

@dataclass
class EducationEntry:
    degree: str = "B.Tech"
    branch: str = "Computer Science"
    institution: str = "Institute of Technology & Science"
    year: str = "2022 - 2026"
    cgpa: str = "8.5 / 10.0"

    def to_dict(self) -> Dict[str, str]:
        return {
            "degree": self.degree,
            "branch": self.branch,
            "institution": self.institution,
            "year": self.year,
            "cgpa": self.cgpa
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "EducationEntry":
        return cls(
            degree=d.get("degree", "B.Tech"),
            branch=d.get("branch", "Computer Science"),
            institution=d.get("institution", "University / College"),
            year=d.get("year", "2022 - 2026"),
            cgpa=d.get("cgpa", "8.0 / 10.0")
        )

@dataclass
class ProjectEntry:
    title: str = "Distributed Task Queue"
    role: str = "Lead Developer"
    tech_stack: str = "Python, Redis, Docker, FastAPI"
    bullets: List[str] = field(default_factory=lambda: [
        "Architected asynchronous task execution engine processing 500+ requests/sec with minimal latency.",
        "Implemented Redis backing queue with automated retry mechanisms and dead-letter error handling.",
        "Containerized the deployment using Docker Compose, reducing local environment setup time by 70%."
    ])
    github_url: str = "github.com/studentprofile/task-queue"
    live_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "role": self.role,
            "tech_stack": self.tech_stack,
            "bullets": self.bullets,
            "github_url": self.github_url,
            "live_url": self.live_url
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "ProjectEntry":
        return cls(
            title=d.get("title", ""),
            role=d.get("role", "Developer"),
            tech_stack=d.get("tech_stack", ""),
            bullets=d.get("bullets", []),
            github_url=d.get("github_url", ""),
            live_url=d.get("live_url", "")
        )

@dataclass
class CertificationEntry:
    title: str = "AWS Certified Cloud Practitioner"
    issuer: str = "Amazon Web Services"
    year: str = "2025"
    credential_id: str = "AWS-CCP-9842"

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "issuer": self.issuer,
            "year": self.year,
            "credential_id": self.credential_id
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "CertificationEntry":
        return cls(
            title=d.get("title", ""),
            issuer=d.get("issuer", ""),
            year=d.get("year", ""),
            credential_id=d.get("credential_id", "")
        )

@dataclass
class AchievementEntry:
    description: str = "Finalist in National Hackathon 2025 among 400+ participating teams."
    category: str = "Competition"
    year: str = "2025"

    def to_dict(self) -> Dict[str, str]:
        return {
            "description": self.description,
            "category": self.category,
            "year": self.year
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "AchievementEntry":
        return cls(
            description=d.get("description", ""),
            category=d.get("category", "General"),
            year=d.get("year", "")
        )

@dataclass
class ResumeData:
    target_career: str = "Software Developer"
    contact: ContactInfo = field(default_factory=ContactInfo)
    career_objective: str = "Aspiring Software Developer eager to leverage algorithmic problem solving and clean design patterns to build reliable, high-performance software applications."
    professional_summary: str = "Passionate computer science student with hands-on experience in full-stack architecture, object-oriented design, and database modeling. Proven track record of developing scalable applications and collaborating in agile team environments."
    technical_skills: Dict[str, List[str]] = field(default_factory=lambda: {
        "Languages": ["Python", "JavaScript", "SQL", "C++"],
        "Frameworks & Libraries": ["React", "FastAPI", "Node.js", "PyTorch"],
        "Developer Tools & Platforms": ["Git", "Docker", "Linux", "VS Code"],
        "Databases & Cloud": ["PostgreSQL", "SQLite", "Redis", "AWS"]
    })
    projects: List[ProjectEntry] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    certifications: List[CertificationEntry] = field(default_factory=list)
    achievements: List[AchievementEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_career": self.target_career,
            "contact": self.contact.to_dict(),
            "career_objective": self.career_objective,
            "professional_summary": self.professional_summary,
            "technical_skills": self.technical_skills,
            "projects": [p.to_dict() for p in self.projects],
            "education": [e.to_dict() for e in self.education],
            "certifications": [c.to_dict() for c in self.certifications],
            "achievements": [a.to_dict() for a in self.achievements]
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "ResumeData":
        if not d:
            return cls()
        return cls(
            target_career=d.get("target_career", "Software Developer"),
            contact=ContactInfo.from_dict(d.get("contact", {})),
            career_objective=d.get("career_objective", ""),
            professional_summary=d.get("professional_summary", ""),
            technical_skills=d.get("technical_skills", {}),
            projects=[ProjectEntry.from_dict(p) for p in d.get("projects", [])],
            education=[EducationEntry.from_dict(e) for e in d.get("education", [])],
            certifications=[CertificationEntry.from_dict(c) for c in d.get("certifications", [])],
            achievements=[AchievementEntry.from_dict(a) for a in d.get("achievements", [])]
        )
