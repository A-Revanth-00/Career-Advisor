from __future__ import annotations
import html
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.career.career_data import get_career_by_id, get_career_by_name
from app.core.paths import (
    RESUME_TEMPLATE_PATH, RESUME_TEMPLATE_MODERN_PATH,
    RESUME_TEMPLATE_ATS_PATH, RESUME_TEMPLATE_COMPACT_PATH
)
from app.database.models import StudentProfile
from app.resume.resume_data import (
    ResumeData, ContactInfo, EducationEntry, ProjectEntry,
    CertificationEntry, AchievementEntry
)

logger = logging.getLogger(__name__)

_TEMPLATES_CACHE: Dict[str, Dict] = {}

def get_resume_template(template_id: str = "modern") -> Dict:
    """Loads a specific resume layout template from data/templates/."""
    global _TEMPLATES_CACHE
    if template_id in _TEMPLATES_CACHE:
        return _TEMPLATES_CACHE[template_id]

    path_map = {
        "modern": RESUME_TEMPLATE_MODERN_PATH,
        "ats_safe": RESUME_TEMPLATE_ATS_PATH,
        "compact": RESUME_TEMPLATE_COMPACT_PATH,
    }
    target_path = path_map.get(template_id, RESUME_TEMPLATE_MODERN_PATH)
    if not target_path.exists():
        target_path = RESUME_TEMPLATE_PATH

    if target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                tpl = json.load(f)
                _TEMPLATES_CACHE[template_id] = tpl
                return tpl
        except Exception as e:
            logger.error("Failed to load template %s: %s", template_id, e)

    fallback_tpl = {
        "id": template_id,
        "name": "Modern Professional",
        "primary_color": "#1e40af",
        "accent_color": "#2563eb",
        "header_color": "#0f172a",
        "text_color": "#1e293b",
        "muted_color": "#475569",
        "font_family": "'Segoe UI', Inter, Roboto, Arial, sans-serif",
        "font_size_base": "13px",
        "padding": "24px 32px",
        "sections_order": [
            "header", "summary", "education", "technical_skills",
            "projects", "certifications", "achievements"
        ]
    }
    _TEMPLATES_CACHE[template_id] = fallback_tpl
    return fallback_tpl

def get_available_templates() -> List[Dict[str, str]]:
    """Returns metadata for all available resume templates."""
    return [
        {"id": "modern", "name": "Modern Professional", "description": "Blue accent, clean hierarchy for tech roles"},
        {"id": "ats_safe", "name": "ATS-Safe Classic", "description": "Monochrome single-column for automated screening"},
        {"id": "compact", "name": "Compact One-Page", "description": "Dense layout with emerald accents for freshers"}
    ]

class ResumeBuilder:
    @classmethod
    def build_from_profile(cls, profile: StudentProfile, career_name_or_id: Optional[str] = None) -> ResumeData:
        """Generates a cohesive, professional resume based on student profile and target career."""
        target_name = career_name_or_id or profile.career_goal or "Software Developer"
        career = get_career_by_id(target_name) or get_career_by_name(target_name)
        display_career = career.name if career else target_name

        # 1. Contact info
        contact = ContactInfo(
            name=profile.name.strip() or "Student Name",
            email=profile.email.strip() or "student@university.edu",
            phone="+1 (555) 234-5678",
            location="Open to Relocation / Remote",
            linkedin=f"linkedin.com/in/{profile.name.lower().replace(' ', '') if profile.name else 'student'}",
            github=f"github.com/{profile.name.lower().replace(' ', '') if profile.name else 'student'}",
            portfolio=""
        )

        # 2. Education
        edu = EducationEntry(
            degree=profile.education or "B.Tech",
            branch=profile.branch or "Computer Science & Engineering",
            institution="University Institute of Technology",
            year="2022 - 2026",
            cgpa=f"{profile.cgpa} / 10.0" if profile.cgpa > 0 else "8.5 / 10.0"
        )

        # 3. Categorize student skills
        skills_dict: Dict[str, List[str]] = {
            "Programming Languages": [],
            "Frameworks & Libraries": [],
            "Databases & Tools": [],
            "Concepts & Systems": []
        }

        lang_keywords = {"python", "javascript", "typescript", "c++", "c#", "c", "java", "go", "rust", "dart", "html5", "css3", "sql", "solidity", "kotlin", "swift", "r"}
        fw_keywords = {"react", "node.js", "express", "fastapi", "django", "pytorch", "tensorflow", "scikit-learn", "flutter", "vue.js", "next.js", "pandas", "numpy", "selenium", "pytest", "cypress", "playwright", "unity", "ros"}
        db_keywords = {"postgresql", "sqlite", "mongodb", "redis", "docker", "kubernetes", "git", "aws", "linux", "power bi", "tableau", "terraform", "ansible", "bash", "wireshark", "postman", "jira", "figma"}

        for s in profile.skills:
            s_clean = s.strip()
            if not s_clean:
                continue
            s_lower = s_clean.lower()
            if any(k in s_lower for k in lang_keywords):
                skills_dict["Programming Languages"].append(s_clean)
            elif any(k in s_lower for k in fw_keywords):
                skills_dict["Frameworks & Libraries"].append(s_clean)
            elif any(k in s_lower for k in db_keywords):
                skills_dict["Databases & Tools"].append(s_clean)
            else:
                skills_dict["Concepts & Systems"].append(s_clean)

        # Fallback if empty
        if not any(skills_dict.values()):
            skills_dict["Programming Languages"] = ["Python", "SQL", "Git"]
            skills_dict["Frameworks & Libraries"] = ["FastAPI", "React"]

        # Clean empty categories
        skills_dict = {k: v for k, v in skills_dict.items() if v}

        # 4. Summary & Objective
        skills_str = ", ".join(profile.skills[:4]) if profile.skills else "software development, problem solving, and modern tooling"
        summary = (
            f"Detail-oriented {profile.education} student specializing in {profile.branch} with foundational expertise in {skills_str}. "
            f"Committed to applying clean software engineering practices, algorithmic rigor, and rapid technical learning to high-impact {display_career} roles."
        )

        objective = (
            f"Aspiring {display_career} seeking a challenging internship or entry-level software engineering role to leverage skills in {skills_str} "
            f"and contribute to building scalable, robust products."
        )

        # 5. Tailored Projects
        projects = cls._build_starter_projects(display_career, profile.skills)

        # 6. Certifications & Achievements
        certs = [
            CertificationEntry(
                title=f"{display_career} Foundations Certification",
                issuer="Online Technical Academy / Coursera",
                year="2025",
                credential_id="CERT-84920"
            )
        ]

        achievements = [
            AchievementEntry(
                description="Recognized on the Academic Dean's Honor List for maintaining top 10% academic standing.",
                category="Academic",
                year="2024"
            ),
            AchievementEntry(
                description="Built and open-sourced developer tool with 100+ active GitHub community stars.",
                category="Open Source",
                year="2025"
            )
        ]

        return ResumeData(
            target_career=display_career,
            contact=contact,
            career_objective=objective,
            professional_summary=summary,
            technical_skills=skills_dict,
            projects=projects,
            education=[edu],
            certifications=certs,
            achievements=achievements
        )

    @staticmethod
    def _build_starter_projects(career_name: str, skills: List[str]) -> List[ProjectEntry]:
        """Provides high-impact bulleted project examples tailored to career path."""
        s_lower = career_name.lower()
        if "ai" in s_lower or "machine learning" in s_lower or "data science" in s_lower:
            return [
                ProjectEntry(
                    title="Intelligent Document Analysis & RAG Assistant",
                    role="Sole Architect",
                    tech_stack="Python, PyTorch, FAISS, LangChain, FastAPI",
                    bullets=[
                        "Developed contextual retrieval-augmented question answering engine processing multi-page technical PDFs in under 400ms.",
                        "Engineered vector search index with cosine similarity ranking, increasing domain answer accuracy by 32%.",
                        "Built REST API with asynchronous streaming endpoints, handling 200+ concurrent requests gracefully."
                    ],
                    github_url="github.com/studentprofile/rag-doc-engine"
                ),
                ProjectEntry(
                    title="Predictive Machine Learning Pipeline with Automated Metrics",
                    role="Data Scientist",
                    tech_stack="Python, Scikit-Learn, Pandas, NumPy, Matplotlib",
                    bullets=[
                        "Trained and evaluated Gradient Boosting & Random Forest models on 50,000+ data records, achieving 89.4% ROC-AUC.",
                        "Implemented cross-validation, hyperparameter tuning, and automated feature selection pipelines.",
                        "Generated interactive visual reports illustrating model precision, recall, and feature importance scores."
                    ],
                    github_url="github.com/studentprofile/ml-prediction-pipeline"
                )
            ]
        elif "frontend" in s_lower or "web" in s_lower or "design" in s_lower or "ui" in s_lower:
            return [
                ProjectEntry(
                    title="Responsive Real-Time Analytics Dashboard",
                    role="Frontend Developer",
                    tech_stack="React, TypeScript, Tailwind CSS, Chart.js, Vite",
                    bullets=[
                        "Engineered modular component library with strict TypeScript interfaces, ensuring 100% type safety and maintainability.",
                        "Optimized rendering performance and state updates, slashing first contentful paint (FCP) time by 45%.",
                        "Implemented dark/light accessibility theme engine conforming strictly to WCAG 2.1 AA standards."
                    ],
                    github_url="github.com/studentprofile/react-analytics-suite"
                ),
                ProjectEntry(
                    title="Interactive E-Commerce Product Platform",
                    role="Full Stack Contributor",
                    tech_stack="JavaScript, HTML5, CSS3, REST APIs, LocalStorage",
                    bullets=[
                        "Designed responsive grid catalog with real-time filtering, keyword search, and dynamic cart state management.",
                        "Integrated RESTful endpoints for catalog data sync with fallback offline client caching mechanisms."
                    ],
                    github_url="github.com/studentprofile/ecommerce-storefront"
                )
            ]
        elif "security" in s_lower or "cyber" in s_lower:
            return [
                ProjectEntry(
                    title="Automated Network Vulnerability & Port Scanner",
                    role="Security Engineer",
                    tech_stack="Python, Scapy, Socket, Nmap, SQLite",
                    bullets=[
                        "Engineered multi-threaded port scanner probing 1,000+ ports/sec with customizable timeout and banner grabbing.",
                        "Built signature matching engine cross-referencing open services with CVE vulnerability feeds.",
                        "Generated comprehensive HTML/JSON compliance audit reports highlighting critical security risks."
                    ],
                    github_url="github.com/studentprofile/vuln-scanner"
                ),
                ProjectEntry(
                    title="Secure Multi-Factor Authentication & Identity Gateway",
                    role="Backend Developer",
                    tech_stack="Python, Argon2, JWT, TOTP, PostgreSQL",
                    bullets=[
                        "Implemented secure password hashing, TOTP two-factor authentication, and refresh token rotation.",
                        "Engineered automated brute-force rate limiter mitigating distributed credential stuffing attacks."
                    ],
                    github_url="github.com/studentprofile/auth-gateway"
                )
            ]
        elif "cloud" in s_lower or "devops" in s_lower or "reliability" in s_lower or "sre" in s_lower:
            return [
                ProjectEntry(
                    title="Automated Cloud Infrastructure & GitOps Pipeline",
                    role="DevOps Engineer",
                    tech_stack="Terraform, AWS, Docker, Kubernetes, GitHub Actions",
                    bullets=[
                        "Provisioned multi-AZ VPC architecture with public/private subnets, NAT Gateways, and RDS cluster using Terraform.",
                        "Configured automated GitHub Actions workflow building Docker containers and deploying via Helm to Kubernetes.",
                        "Deployed Prometheus & Grafana telemetry stack tracking cluster resource metrics and error rate alerts."
                    ],
                    github_url="github.com/studentprofile/gitops-infra"
                ),
                ProjectEntry(
                    title="Microservices Health Telemetry & Logging Engine",
                    role="Infrastructure Engineer",
                    tech_stack="Python, Redis, Docker, Prometheus",
                    bullets=[
                        "Built asynchronous health check daemon probing 15+ internal services and publishing real-time uptime metrics.",
                        "Implemented automated alert dispatching to Slack and webhook endpoints upon latency degradation."
                    ],
                    github_url="github.com/studentprofile/service-telemetry"
                )
            ]
        else:
            return [
                ProjectEntry(
                    title="Distributed Task Orchestration & Scheduling Engine",
                    role="Backend Developer",
                    tech_stack="Python, PostgreSQL, Redis, Docker, FastAPI",
                    bullets=[
                        "Architected scalable asynchronous background worker system executing 500+ periodic jobs with automated retry queues.",
                        "Designed relational PostgreSQL schema with indexing and foreign keys, reducing query execution time by 38%.",
                        "Configured Docker container deployment pipelines with health monitoring endpoints and structured JSON logging."
                    ],
                    github_url="github.com/studentprofile/task-orchestrator"
                ),
                ProjectEntry(
                    title="Secure RESTful Microservice API with JWT Authentication",
                    role="Software Developer",
                    tech_stack="Python, SQLite, PyTest, Git",
                    bullets=[
                        "Built robust authentication microservice with bcrypt password hashing, token validation, and rate limiting.",
                        "Wrote comprehensive unit and integration test suite with 92% code coverage using PyTest."
                    ],
                    github_url="github.com/studentprofile/secure-api-auth"
                )
            ]

    @classmethod
    def export_markdown(cls, resume: ResumeData) -> str:
        """Exports resume in clean standard Markdown format."""
        c = resume.contact
        md = []
        md.append(f"# {c.name}\n")
        contacts = [c.email, c.phone, c.location, c.linkedin, c.github]
        md.append(f"**{' | '.join(x for x in contacts if x)}**\n")
        md.append("---\n")

        if resume.professional_summary:
            md.append("## Professional Summary\n")
            md.append(f"{resume.professional_summary}\n")

        if resume.education:
            md.append("## Education\n")
            for e in resume.education:
                md.append(f"- **{e.degree} in {e.branch}** | {e.institution} ({e.year}) — *CGPA: {e.cgpa}*")
            md.append("")

        if resume.technical_skills:
            md.append("## Technical Skills\n")
            for cat, skill_list in resume.technical_skills.items():
                if skill_list:
                    md.append(f"- **{cat}:** {', '.join(skill_list)}")
            md.append("")

        if resume.projects:
            md.append("## Technical Projects\n")
            for p in resume.projects:
                links = []
                if p.github_url:
                    links.append(f"[{p.github_url}](https://{p.github_url})")
                link_str = f" | {', '.join(links)}" if links else ""
                md.append(f"### {p.title} — *{p.role}* ({p.tech_stack}){link_str}")
                for b in p.bullets:
                    md.append(f"- {b}")
                md.append("")

        if resume.certifications:
            md.append("## Certifications\n")
            for cert in resume.certifications:
                md.append(f"- **{cert.title}** — {cert.issuer} ({cert.year})")
            md.append("")

        if resume.achievements:
            md.append("## Achievements & Honors\n")
            for a in resume.achievements:
                md.append(f"- {a.description} ({a.year})")
            md.append("")

        return "\n".join(md)

    @classmethod
    def export_html(cls, resume: ResumeData, template_id: str = "modern") -> str:
        """Exports resume in clean, styled HTML configured by selected layout template."""
        tpl = get_resume_template(template_id)
        c = resume.contact

        primary_col = tpl.get("primary_color", "#1e40af")
        accent_col = tpl.get("accent_color", "#2563eb")
        text_col = tpl.get("text_color", "#1e293b")
        header_col = tpl.get("header_color", "#0f172a")
        muted_col = tpl.get("muted_color", "#475569")
        font_fam = tpl.get("font_family", "'Segoe UI', Arial, sans-serif")
        font_size = tpl.get("font_size_base", "13px")
        padding_val = tpl.get("padding", "24px 32px")
        header_align = tpl.get("header_align", "center")
        divider_border = tpl.get("section_divider", f"1px solid #cbd5e1")
        sections_order = tpl.get("sections_order", ["header", "summary", "education", "technical_skills", "projects", "certifications", "achievements"])

        # Contacts formatting
        sep = " | " if template_id == "ats_safe" else " &bull; "
        contacts = [
            f"<span>{html.escape(c.email)}</span>" if c.email else "",
            f"<span>{html.escape(c.phone)}</span>" if c.phone else "",
            f"<span>{html.escape(c.location)}</span>" if c.location else "",
            f"<span>{html.escape(c.linkedin)}</span>" if c.linkedin else "",
            f"<span>{html.escape(c.github)}</span>" if c.github else ""
        ]
        contact_bar = sep.join(x for x in contacts if x)

        # Section render blocks
        section_html_blocks: Dict[str, str] = {}

        # 1. Header
        if template_id == "ats_safe":
            hdr_bottom = "border-bottom: 2px solid #000000; padding-bottom: 8px; margin-bottom: 14px;"
            name_style = "font-size: 22px; font-weight: bold; letter-spacing: 0.5px; color: #000000; margin-bottom: 4px; text-transform: uppercase;"
        elif template_id == "compact":
            hdr_bottom = f"border-bottom: 2px solid {primary_col}; padding-bottom: 8px; margin-bottom: 12px;"
            name_style = f"font-size: 20px; font-weight: 800; color: {header_col}; margin-bottom: 3px;"
        else:
            hdr_bottom = f"border-bottom: 2px solid {accent_col}; padding-bottom: 12px; margin-bottom: 16px;"
            name_style = f"font-size: 24px; font-weight: 700; letter-spacing: 0.5px; color: {header_col}; margin-bottom: 4px;"

        section_html_blocks["header"] = f"""
        <div style="text-align: {header_align}; {hdr_bottom}">
            <div style="{name_style}">{html.escape(c.name)}</div>
            <div style="font-size: 12px; color: {muted_col};">{contact_bar}</div>
        </div>
        """

        # Section Title Helper
        def make_title(title_text: str) -> str:
            if template_id == "ats_safe":
                return f"""<div style="font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; color: #000000; border-bottom: 1px solid #000000; padding-bottom: 2px; margin-top: 12px; margin-bottom: 6px;">{title_text}</div>"""
            elif template_id == "compact":
                return f"""<div style="font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: {primary_col}; border-bottom: 1px solid #a7f3d0; padding-bottom: 2px; margin-top: 10px; margin-bottom: 5px;">{title_text}</div>"""
            else:
                return f"""<div style="font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: {primary_col}; border-bottom: {divider_border}; padding-bottom: 3px; margin-top: 14px; margin-bottom: 8px;">{title_text}</div>"""

        # 2. Professional Summary
        if resume.professional_summary:
            section_html_blocks["summary"] = f"""
            {make_title("Professional Summary")}
            <div style="font-size: {font_size}; color: {text_col}; line-height: 1.45; text-align: justify;">{html.escape(resume.professional_summary)}</div>
            """

        # 3. Education
        edu_html = ""
        for e in resume.education:
            if template_id == "ats_safe":
                edu_html += f"""
                <div style="margin-bottom: 6px; font-size: {font_size};">
                    <strong>{html.escape(e.degree)} in {html.escape(e.branch)}</strong> &mdash; {html.escape(e.institution)} ({html.escape(e.year)}) | <em>CGPA: {html.escape(e.cgpa)}</em>
                </div>
                """
            else:
                edu_html += f"""
                <div style="margin-bottom: 6px; display: flex; justify-content: space-between; align-items: baseline; font-size: {font_size};">
                    <div>
                        <strong style="color: {header_col};">{html.escape(e.degree)} in {html.escape(e.branch)}</strong> &mdash; 
                        <span style="color: {muted_col};">{html.escape(e.institution)}</span>
                    </div>
                    <div style="text-align: right; color: {muted_col}; font-size: 12px;">
                        <span>{html.escape(e.year)}</span> &bull; <strong>CGPA: {html.escape(e.cgpa)}</strong>
                    </div>
                </div>
                """
        section_html_blocks["education"] = f"""
        {make_title("Education")}
        {edu_html}
        """

        # 4. Technical Skills
        skills_html = ""
        for cat, slist in resume.technical_skills.items():
            if slist:
                skills_html += f"""
                <div style="margin-bottom: 4px; font-size: {font_size}; line-height: 1.4;">
                    <strong style="color: {header_col};">{html.escape(cat)}:</strong> 
                    <span style="color: {text_col};">{html.escape(', '.join(slist))}</span>
                </div>
                """
        section_html_blocks["technical_skills"] = f"""
        {make_title("Technical Skills")}
        {skills_html}
        """

        # 5. Projects
        proj_html = ""
        for p in resume.projects:
            bullets_li = "".join(f"<li style='margin-bottom: 3px;'>{html.escape(b)}</li>" for b in p.bullets)
            link_display = f"<span style='color: {accent_col}; font-size: 12px; font-family: monospace;'> | {html.escape(p.github_url)}</span>" if p.github_url else ""
            proj_html += f"""
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 2px;">
                    <div>
                        <strong style="font-size: {font_size}; color: {header_col};">{html.escape(p.title)}</strong> 
                        <span style="color: {muted_col}; font-size: 12px;"> &mdash; <em>{html.escape(p.role)}</em></span>
                        {link_display}
                    </div>
                </div>
                <div style="font-size: 11.5px; color: {muted_col}; font-style: italic; margin-bottom: 3px;">
                    Tech Stack: {html.escape(p.tech_stack)}
                </div>
                <ul style="margin: 0; padding-left: 18px; color: {text_col}; font-size: {font_size}; line-height: 1.4;">
                    {bullets_li}
                </ul>
            </div>
            """
        section_html_blocks["projects"] = f"""
        {make_title("Technical Projects")}
        {proj_html}
        """

        # 6. Certifications
        if resume.certifications:
            certs_html = "".join(
                f"<li style='margin-bottom: 3px;'><strong>{html.escape(cert.title)}</strong> &mdash; {html.escape(cert.issuer)} ({html.escape(cert.year)})</li>"
                for cert in resume.certifications
            )
            section_html_blocks["certifications"] = f"""
            {make_title("Certifications")}
            <ul style="margin: 0; padding-left: 18px; font-size: {font_size}; color: {text_col}; line-height: 1.4;">{certs_html}</ul>
            """
        else:
            section_html_blocks["certifications"] = ""

        # 7. Achievements
        if resume.achievements:
            achieve_html = "".join(
                f"<li style='margin-bottom: 3px;'>{html.escape(a.description)} ({html.escape(a.year)})</li>"
                for a in resume.achievements
            )
            section_html_blocks["achievements"] = f"""
            {make_title("Achievements & Honors")}
            <ul style="margin: 0; padding-left: 18px; font-size: {font_size}; color: {text_col}; line-height: 1.4;">{achieve_html}</ul>
            """
        else:
            section_html_blocks["achievements"] = ""

        # Assemble body based on template section order
        body_content = "".join(section_html_blocks.get(sec, "") for sec in sections_order)

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        font-family: {font_fam};
        color: {text_col};
        background: #ffffff;
        margin: 0;
        padding: {padding_val};
        line-height: 1.45;
        font-size: {font_size};
    }}
    ul {{
        margin: 0;
        padding-left: 18px;
    }}
    li {{
        margin-bottom: 3px;
    }}
</style>
</head>
<body>
{body_content}
</body>
</html>"""

    @classmethod
    def export_plain_text(cls, resume: ResumeData) -> str:
        """Exports plain ASCII text format."""
        c = resume.contact
        lines = []
        lines.append(f"=== {c.name.upper()} ===")
        lines.append(f"Email: {c.email} | Phone: {c.phone} | Location: {c.location}")
        lines.append(f"LinkedIn: {c.linkedin} | GitHub: {c.github}\n")
        lines.append("-" * 60)

        lines.append("PROFESSIONAL SUMMARY")
        lines.append(resume.professional_summary + "\n")

        lines.append("EDUCATION")
        for e in resume.education:
            lines.append(f"* {e.degree} in {e.branch} - {e.institution} ({e.year}) | CGPA: {e.cgpa}")
        lines.append("")

        lines.append("TECHNICAL SKILLS")
        for cat, slist in resume.technical_skills.items():
            lines.append(f"* {cat}: {', '.join(slist)}")
        lines.append("")

        lines.append("TECHNICAL PROJECTS")
        for p in resume.projects:
            lines.append(f"* {p.title} ({p.role}) - Stack: {p.tech_stack}")
            for b in p.bullets:
                lines.append(f"  - {b}")
        lines.append("")

        if resume.certifications:
            lines.append("CERTIFICATIONS")
            for cert in resume.certifications:
                lines.append(f"* {cert.title} - {cert.issuer} ({cert.year})")
            lines.append("")

        return "\n".join(lines)

