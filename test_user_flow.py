from __future__ import annotations
import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication, QMessageBox

# Mock QMessageBox methods for non-interactive test run
QMessageBox.information = lambda *args, **kwargs: QMessageBox.Ok
QMessageBox.warning = lambda *args, **kwargs: QMessageBox.Ok
QMessageBox.critical = lambda *args, **kwargs: QMessageBox.Ok
QMessageBox.question = lambda *args, **kwargs: QMessageBox.Yes

from app.database.database import init_database
from app.database.models import StudentProfile
from app.database.repository import ProfileRepository
from app.career.career_data import load_career_database, get_career_by_id
from app.career.matcher import CareerMatcher
from app.career.skill_gap import SkillGapAnalyzer
from app.roadmap.roadmap_generator import RoadmapGenerator
from app.roadmap.planner import RoadmapPlanner
from app.roadmap.progress import RoadmapProgressTracker
from app.resume.resume_builder import ResumeBuilder
from app.resume.ats_analyzer import LocalATSAnalyzer
from app.ui.main_window import MainWindow

def run_main_user_flow_simulation():
    print("==================================================")
    print("STEP 1: Application Launch & Initialization")
    print("==================================================")
    app = QApplication.instance() or QApplication(sys.argv)
    init_database()
    window = MainWindow()
    assert window is not None, "Failed to launch MainWindow"
    print("✔ Application started offline successfully.")

    print("\n==================================================")
    print("STEP 2: Navigate to Dashboard & Verify Initial State")
    print("==================================================")
    window.switch_page(0)
    assert window.stacked_widget.currentIndex() == 0
    print(f"✔ Dashboard loaded. Active Title: {window.page_title_lbl.text()}")

    print("\n==================================================")
    print("STEP 3: Navigate to My Profile & Save Student Info")
    print("==================================================")
    window.switch_page(1)
    assert window.stacked_widget.currentIndex() == 1
    
    # Enter Profile
    profile_view = window.profile_view
    profile_view.name_edit.setText("David Chen")
    profile_view.email_edit.setText("david.chen@cs.stanford.edu")
    profile_view.degree_combo.setCurrentText("B.Tech")
    profile_view.branch_combo.setCurrentText("Computer Science")
    profile_view.cgpa_spin.setValue(8.9)
    profile_view.skills_edit.setText("Python, JavaScript, React, SQL, Git, Linux, Docker")
    profile_view.interests_edit.setText("Full Stack Development, Web Services, System Design")
    profile_view.goal_combo.setCurrentText("Full Stack Developer")
    profile_view.hours_spin.setValue(3.0)
    profile_view.days_spin.setValue(5)
    
    # Trigger Save
    profile_view.save_profile()
    
    saved = ProfileRepository.get_profile()
    assert saved is not None and saved.name == "David Chen"
    print(f"✔ Profile saved: {saved.name} ({saved.education} {saved.branch}), Target: {saved.career_goal}, {saved.weekly_hours}h/week")

    print("\n==================================================")
    print("STEP 4: Navigate to Career Guide & Analyze Careers")
    print("==================================================")
    window.switch_page(2)
    assert window.stacked_widget.currentIndex() == 2
    
    assessment_view = window.assessment_view
    assessment_view.run_analysis()
    
    ranked = assessment_view.all_results
    assert len(ranked) >= 12, "Should have ranked 12+ careers"
    print(f"✔ Analyzed {len(ranked)} careers. Top 5 recommendations:")
    for idx, r in enumerate(ranked[:5], 1):
        print(f"   {idx}. {r.career_name} — Score: {r.score}% ({r.match_level}) [Matched: {len(r.matched_skills)}/{len(r.career.required_skills)} skills]")

    top_rec = ranked[0]

    print("\n==================================================")
    print("STEP 5: Open Career Deep Dive & Skill Gap Analysis")
    print("==================================================")
    career_target = get_career_by_id(top_rec.career_id)
    assert career_target is not None
    gap = SkillGapAnalyzer.analyze(saved, career_target)
    print(f"✔ Career: {career_target.name} ({career_target.category})")
    print(f"   - Skill Readiness: {gap.skill_readiness}%")
    print(f"   - Overall Readiness: {gap.overall_readiness}% ({gap.readiness_level})")
    print(f"   - Matched Skills: {gap.matched_skills}")
    print(f"   - Missing Skills: {gap.missing_skills}")
    print(f"   - Action Steps: {gap.actionable_steps[0]}")

    print("\n==================================================")
    print("STEP 6: Navigate to Roadmap & Generate Weekly Plan")
    print("==================================================")
    window.switch_page(3)
    assert window.stacked_widget.currentIndex() == 3
    
    roadmap_view = window.roadmap_view
    roadmap_view.set_target_career(career_target.id)
    
    plan = roadmap_view.current_plan
    roadmap = roadmap_view.current_roadmap
    assert plan is not None and roadmap is not None
    print(f"✔ Generated Roadmap for {roadmap.career_name}:")
    print(f"   - Total Hours: {roadmap.total_hours}h across {plan.total_estimated_weeks} weeks")
    print(f"   - Phase 1 (Foundation): {len(roadmap.phase_1_tasks)} tasks")
    print(f"   - Phase 2 (Core Skills): {len(roadmap.phase_2_tasks)} tasks")
    print(f"   - Phase 3 (Projects): {len(roadmap.phase_3_tasks)} tasks")
    print(f"   - Phase 4 (Career Prep): {len(roadmap.phase_4_tasks)} tasks")

    # Mark first task complete and verify progress
    t1 = roadmap.tasks[0]
    roadmap_view._on_task_toggled(t1.id, True)
    prog = RoadmapProgressTracker.get_progress(roadmap)
    assert t1.id in prog.completed_task_ids
    print(f"✔ Completed task '{t1.title}' -> Progress updated to {prog.percentage}%")

    print("\n==================================================")
    print("STEP 7: Navigate to Resume Studio & ATS Analysis")
    print("==================================================")
    window.switch_page(4)
    assert window.stacked_widget.currentIndex() == 4
    
    resume_view = window.resume_view
    resume_view.set_target_career(career_target.id)
    resume = resume_view.current_resume
    assert resume is not None
    print(f"✔ Resume auto-tailored for {resume.target_career}")
    print(f"   - Candidate: {resume.contact.name} ({resume.contact.email})")
    print(f"   - Education: {resume.education[0].degree} in {resume.education[0].branch}")
    print(f"   - Projects: {len(resume.projects)} portfolio projects included")

    # ATS Screening
    ats = resume_view.ats_result
    assert ats is not None
    print(f"✔ ATS Heuristic Analysis: Score={ats.score}/100 (Grade: {ats.grade})")
    print(f"   - Strengths: {ats.strengths[:2]}")
    if ats.improvements:
        print(f"   - Suggested Improvements: {ats.improvements[:2]}")

    print("\n==================================================")
    print("STEP 8: Return to Dashboard & Verify Live Status")
    print("==================================================")
    window.switch_page(0)
    dash = window.dashboard_view
    dash.refresh_dashboard()
    print(f"✔ Dashboard live metrics:")
    print(f"   - Career Match: {dash.card_match.lbl_val.text()} ({dash.card_match.lbl_sub.text()})")
    print(f"   - Career Readiness: {dash.card_readiness.lbl_val.text()} ({dash.card_readiness.lbl_sub.text()})")
    print(f"   - Roadmap Progress: {dash.card_roadmap.lbl_val.text()} ({dash.card_roadmap.lbl_sub.text()})")
    print(f"   - Resume ATS: {dash.card_ats.lbl_val.text()} ({dash.card_ats.lbl_sub.text()})")

    print("\n>>> FULL END-TO-END MAIN USER FLOW COMPLETED SUCCESSFULLY! <<<")
    window.close()

if __name__ == "__main__":
    run_main_user_flow_simulation()
