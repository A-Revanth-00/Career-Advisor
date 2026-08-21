from __future__ import annotations
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
from app.database.database import get_connection
from app.database.models import StudentProfile, RoadmapTaskProgress
from app.core.utils import safe_json_dumps, safe_json_loads

class ProfileRepository:
    @staticmethod
    def get_profile() -> Optional[StudentProfile]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_profile ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return StudentProfile.from_row(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def save_or_update_profile(profile: StudentProfile) -> StudentProfile:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            now_str = datetime.now().isoformat()
            
            existing = ProfileRepository.get_profile()
            if existing and existing.id:
                profile.id = existing.id
                profile.updated_at = now_str
                cursor.execute("""
                    UPDATE student_profile
                    SET name = ?, email = ?, education = ?, branch = ?, cgpa = ?,
                        skills = ?, interests = ?, career_goal = ?, hours_per_day = ?,
                        days_per_week = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    profile.name.strip(),
                    profile.email.strip(),
                    profile.education.strip(),
                    profile.branch.strip(),
                    profile.cgpa,
                    safe_json_dumps(profile.skills),
                    safe_json_dumps(profile.interests),
                    profile.career_goal.strip(),
                    profile.hours_per_day,
                    profile.days_per_week,
                    profile.updated_at,
                    profile.id
                ))
            else:
                profile.created_at = now_str
                profile.updated_at = now_str
                cursor.execute("""
                    INSERT INTO student_profile (
                        name, email, education, branch, cgpa, skills,
                        interests, career_goal, hours_per_day, days_per_week,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.name.strip(),
                    profile.email.strip(),
                    profile.education.strip(),
                    profile.branch.strip(),
                    profile.cgpa,
                    safe_json_dumps(profile.skills),
                    safe_json_dumps(profile.interests),
                    profile.career_goal.strip(),
                    profile.hours_per_day,
                    profile.days_per_week,
                    profile.created_at,
                    profile.updated_at
                ))
                profile.id = cursor.lastrowid

            conn.commit()
            return profile
        finally:
            conn.close()

class RoadmapRepository:
    @staticmethod
    def get_completed_tasks(career_id: str) -> Set[str]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT task_id FROM roadmap_progress WHERE career_id = ? AND completed = 1",
                (career_id,)
            )
            return {row["task_id"] for row in cursor.fetchall()}
        finally:
            conn.close()

    @staticmethod
    def set_task_status(career_id: str, task_id: str, completed: bool, notes: str = "") -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            now_str = datetime.now().isoformat() if completed else None
            cursor.execute("""
                INSERT INTO roadmap_progress (career_id, task_id, completed, completed_at, notes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(career_id, task_id) DO UPDATE SET
                    completed = excluded.completed,
                    completed_at = excluded.completed_at,
                    notes = excluded.notes
            """, (career_id, task_id, 1 if completed else 0, now_str, notes))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def reset_progress(career_id: str) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM roadmap_progress WHERE career_id = ?", (career_id,))
            conn.commit()
        finally:
            conn.close()

class ResumeRepository:
    @staticmethod
    def get_resume(career_target: str = "") -> Optional[Dict]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if career_target:
                cursor.execute(
                    "SELECT resume_data FROM saved_resumes WHERE career_target = ? ORDER BY id DESC LIMIT 1",
                    (career_target,)
                )
            else:
                cursor.execute("SELECT resume_data FROM saved_resumes ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row and row["resume_data"]:
                return safe_json_loads(row["resume_data"], {})
            return None
        finally:
            conn.close()

    @staticmethod
    def save_resume(career_target: str, resume_data: Dict, profile_id: Optional[int] = None) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            now_str = datetime.now().isoformat()
            data_str = safe_json_dumps(resume_data)
            cursor.execute("""
                INSERT INTO saved_resumes (profile_id, career_target, resume_data, updated_at)
                VALUES (?, ?, ?, ?)
            """, (profile_id, career_target, data_str, now_str))
            conn.commit()
        finally:
            conn.close()
