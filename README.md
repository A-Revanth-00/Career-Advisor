# CAREER ADVISOR

**Professional Offline-First Desktop Career Planning Application for Students**

---

## Overview

**CAREER ADVISOR** is a desktop application built with **Python 3.11+**, **PySide6**, and **SQLite**. It operates 100% offline without mandatory internet connectivity, external APIs, or cloud database dependencies.

### Primary Capabilities:
1. **Student Profile Management**: Academic credentials, technical skills, interests, and weekly study availability.
2. **Deterministic Career Recommendation Engine**: Transparent mathematical weighting (Skills 50%, Interests 35%, Education 15%) across 12+ industry career paths.
3. **Skill Gap & Readiness Analyzer**: Quantifies matched vs. missing skills, educational compatibility, and actionable progression steps.
4. **4-Phase Personalized Roadmap Planner**: Foundations, Core Skills, Portfolio Projects, and Career Prep scheduled into constrained weekly workloads.
5. **Interactive Roadmap Progress Tracking**: Dynamic completion percentages and state persistence in local SQLite database.
6. **Professional Resume Studio**: Auto-tailors ATS-compliant resumes with real-time editing and multi-format exports (HTML, Markdown, Plain Text).
7. **Local Heuristic ATS Analyzer**: Evaluates contact completeness, keyword density, action verbs, and quantifiable impact metrics.
8. **Offline Learning Resource Hub**: Curated courses, documentation, and exercises categorized by skill, provider, and difficulty level.

---

## Tech Stack & Architecture

- **GUI Framework**: PySide6 (Qt for Python)
- **Local Persistence**: SQLite3 with non-destructive PRAGMA schema migrations
- **Offline Data**: Structured JSON knowledge bases (`data/career_database.json`, `data/learning_resources.json`)
- **Language**: Python 3.11+

```
Desktop App (PySide6 UI)
  ↓
Application Services & Engines (Matcher, Gap Analyzer, Roadmap Planner, Resume Studio)
  ↓
SQLite Database (career_advisor.db) + Offline JSON Catalogs
```

---

## Project Structure

```
CareerAdvisor/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── paths.py
│   │   └── utils.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   ├── career/
│   │   ├── __init__.py
│   │   ├── career_data.py
│   │   ├── matcher.py
│   │   └── skill_gap.py
│   ├── roadmap/
│   │   ├── __init__.py
│   │   ├── roadmap_generator.py
│   │   ├── planner.py
│   │   └── progress.py
│   ├── resume/
│   │   ├── __init__.py
│   │   ├── resume_data.py
│   │   ├── resume_builder.py
│   │   └── ats_analyzer.py
│   ├── learning/
│   │   ├── __init__.py
│   │   ├── resource_database.py
│   │   └── learning_planner.py
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py
│       ├── theme.py
│       ├── dashboard/
│       │   ├── __init__.py
│       │   └── dashboard_view.py
│       ├── profile/
│       │   ├── __init__.py
│       │   └── profile.py
│       ├── career/
│       │   ├── __init__.py
│       │   ├── assessment_view.py
│       │   ├── results_view.py
│       │   └── career_detail_view.py
│       ├── roadmap/
│       │   ├── __init__.py
│       │   └── roadmap_view.py
│       ├── resume/
│       │   ├── __init__.py
│       │   ├── resume_view.py
│       │   └── resume_preview.py
│       ├── learning/
│       │   ├── __init__.py
│       │   └── learning_view.py
│       └── settings/
│           ├── __init__.py
│           └── settings_view.py
├── data/
│   ├── career_database.json
│   ├── learning_resources.json
│   └── templates/
│       └── resume_template.json
├── exports/
├── requirements.txt
├── test_app.py
└── test_user_flow.py
```

---

## Installation & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python -m app.main
```

### 3. Run Automated Tests
```bash
python test_app.py
python test_user_flow.py
```
