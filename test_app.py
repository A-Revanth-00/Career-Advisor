from __future__ import annotations
import os
import sys

# Ensure offscreen Qt execution for automated testing environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import unittest
from PySide6.QtWidgets import QApplication
from app.core.paths import BASE_DIR, DATABASE_PATH, CAREER_DATABASE_PATH, LEARNING_RESOURCES_PATH
from app.core.utils import normalize_skill, validate_cgpa, validate_hours_and_days, parse_comma_separated
from app.database.database import init_database
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository, RoadmapRepository, ResumeRepository
from app.career.career_data import load_career_database, get_career_by_id, get_career_by_name
from app.career.matcher import CareerMatcher
from app.career.skill_gap import SkillGapAnalyzer
from app.roadmap.roadmap_generator import RoadmapGenerator
from app.roadmap.planner import RoadmapPlanner
from app.roadmap.progress import RoadmapProgressTracker
from app.resume.resume_builder import ResumeBuilder
from app.resume.ats_analyzer import LocalATSAnalyzer
from app.learning.resource_database import load_learning_resources, filter_resources
from app.learning.learning_planner import LearningPlanner
from app.ui.main_window import MainWindow

class TestCareerAdvisor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        init_database()

    def test_01_paths_and_json_databases(self):
        self.assertTrue(CAREER_DATABASE_PATH.exists(), "Career database JSON missing")
        self.assertTrue(LEARNING_RESOURCES_PATH.exists(), "Learning resources JSON missing")
        
        careers = load_career_database()
        self.assertGreaterEqual(len(careers), 12, "Should have at least 12 careers")
        career_names = [c.name for c in careers]
        self.assertIn("AI Engineer", career_names)
        self.assertIn("Software Developer", career_names)
        self.assertIn("Backend Developer", career_names)
        self.assertIn("Frontend Developer", career_names)
        self.assertIn("Data Scientist", career_names)
        self.assertIn("Cybersecurity Engineer", career_names)
        self.assertIn("Cloud Engineer", career_names)
        self.assertIn("DevOps Engineer", career_names)
        self.assertIn("Mobile Developer", career_names)
        self.assertIn("Full Stack Developer", career_names)
        self.assertIn("Data Analyst", career_names)
        self.assertIn("Machine Learning Engineer", career_names)

    def test_02_profile_repository(self):
        prof = StudentProfile(
            name="Jane Doe",
            email="jane.doe@univ.edu",
            education="B.Tech",
            branch="Computer Science",
            cgpa=9.1,
            skills=["Python", "PyTorch", "Deep Learning", "SQL", "Git"],
            interests=["Artificial Intelligence", "Machine Learning"],
            career_goal="AI Engineer",
            hours_per_day=3.0,
            days_per_week=5
        )
        saved = ProfileRepository.save_or_update_profile(prof)
        self.assertIsNotNone(saved.id)
        
        retrieved = ProfileRepository.get_profile()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Jane Doe")
        self.assertEqual(retrieved.weekly_hours, 15.0)
        self.assertEqual(len(retrieved.skills), 5)

    def test_03_career_matcher_deterministic_scoring(self):
        prof = ProfileRepository.get_profile()
        ranked = CareerMatcher.rank_careers(prof)
        self.assertGreater(len(ranked), 0)
        
        # AI Engineer should score near the top for Jane Doe
        top_match = ranked[0]
        self.assertIn(top_match.career_id, ["ai_engineer", "ml_engineer", "data_scientist"])
        self.assertGreaterEqual(top_match.score, 40.0)
        self.assertIsInstance(top_match.matched_skills, list)
        self.assertIsInstance(top_match.missing_skills, list)

    def test_04_skill_gap_analysis(self):
        prof = ProfileRepository.get_profile()
        ai_career = get_career_by_id("ai_engineer")
        self.assertIsNotNone(ai_career)
        
        gap = SkillGapAnalyzer.analyze(prof, ai_career)
        self.assertGreater(gap.skill_readiness, 0.0)
        self.assertGreater(gap.overall_readiness, 0.0)
        self.assertTrue(len(gap.actionable_steps) >= 3)

    def test_05_roadmap_generation_and_planner(self):
        prof = ProfileRepository.get_profile()
        ai_career = get_career_by_id("ai_engineer")
        roadmap = RoadmapGenerator.generate(prof, ai_career)
        
        self.assertGreater(len(roadmap.tasks), 0)
        self.assertGreater(roadmap.total_hours, 0.0)
        self.assertTrue(any(t.phase_num == 1 for t in roadmap.tasks))
        self.assertTrue(any(t.phase_num == 2 for t in roadmap.tasks))
        self.assertTrue(any(t.phase_num == 3 for t in roadmap.tasks))
        self.assertTrue(any(t.phase_num == 4 for t in roadmap.tasks))

        # Test weekly scheduler with capacity constraint
        plan = RoadmapPlanner.plan(roadmap, prof.hours_per_day, prof.days_per_week)
        self.assertEqual(plan.weekly_hours_capacity, 15.0)
        self.assertGreater(plan.total_estimated_weeks, 0)
        for w in plan.weeks:
            self.assertLessEqual(w.total_allocated_hours, plan.weekly_hours_capacity + 0.01)

    def test_06_roadmap_progress_persistence(self):
        prof = ProfileRepository.get_profile()
        ai_career = get_career_by_id("ai_engineer")
        roadmap = RoadmapGenerator.generate(prof, ai_career)
        
        first_task = roadmap.tasks[0]
        RoadmapProgressTracker.set_task_completed(ai_career.id, first_task.id, True)
        
        progress = RoadmapProgressTracker.get_progress(roadmap)
        self.assertIn(first_task.id, progress.completed_task_ids)
        self.assertGreater(progress.percentage, 0.0)
        
        # Reset and verify
        RoadmapProgressTracker.reset_career_progress(ai_career.id)
        progress_after = RoadmapProgressTracker.get_progress(roadmap)
        self.assertEqual(progress_after.percentage, 0.0)

    def test_07_resume_builder_and_ats_screening(self):
        prof = ProfileRepository.get_profile()
        resume = ResumeBuilder.build_from_profile(prof, "ai_engineer")
        self.assertEqual(resume.contact.name, "Jane Doe")
        self.assertGreaterEqual(len(resume.projects), 2)
        
        html_out = ResumeBuilder.export_html(resume)
        self.assertIn("Jane Doe", html_out)
        self.assertIn("Professional Summary", html_out)
        
        ats_res = LocalATSAnalyzer.analyze(resume)
        self.assertGreaterEqual(ats_res.score, 60)
        self.assertIn(ats_res.grade, ["A+", "A", "B", "C", "D"])
        self.assertGreater(len(ats_res.strengths), 0)

    def test_08_learning_hub_and_curriculum(self):
        prof = ProfileRepository.get_profile()
        ai_career = get_career_by_id("ai_engineer")
        resources = load_learning_resources()
        self.assertGreater(len(resources), 0)
        
        filtered = filter_resources(skill_filter="Python", difficulty_filter="Beginner")
        self.assertGreater(len(filtered), 0)
        
        curriculum = LearningPlanner.generate_curriculum(prof, ai_career)
        self.assertGreater(len(curriculum), 0)

    def test_09_main_window_and_navigation(self):
        window = MainWindow()
        self.assertIsNotNone(window)
        
        # Test switching across all 7 tabs
        for idx in range(7):
            window.switch_page(idx)
            self.assertEqual(window.stacked_widget.currentIndex(), idx)

        # Test profile save signal propagation
        demo_prof = StudentProfile(
            name="Testing User",
            email="test@univ.edu",
            skills=["JavaScript", "React"],
            career_goal="Frontend Developer"
        )
        window._on_profile_saved(demo_prof)
        self.assertIn("Testing User", window.profile_badge.text())
        window.close()

if __name__ == "__main__":
    unittest.main()
