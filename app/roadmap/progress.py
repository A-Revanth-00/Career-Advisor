from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set
from app.database.repository import RoadmapRepository
from app.roadmap.roadmap_generator import Roadmap, RoadmapTask

@dataclass
class RoadmapProgressState:
    career_id: str
    total_tasks: int
    completed_tasks_count: int
    total_hours: float
    completed_hours: float
    percentage: float
    completed_task_ids: Set[str] = field(default_factory=set)
    phase_progress: Dict[int, float] = field(default_factory=dict)

class RoadmapProgressTracker:
    @classmethod
    def get_progress(cls, roadmap: Roadmap) -> RoadmapProgressState:
        """Retrieves and computes dynamic progress metrics for a given roadmap."""
        completed_ids = RoadmapRepository.get_completed_tasks(roadmap.career_id)
        
        total_tasks = len(roadmap.tasks)
        completed_count = 0
        total_hours = roadmap.total_hours
        completed_hours = 0.0

        phase_total_hours: Dict[int, float] = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        phase_completed_hours: Dict[int, float] = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}

        for task in roadmap.tasks:
            phase_total_hours[task.phase_num] = phase_total_hours.get(task.phase_num, 0.0) + task.estimated_hours
            if task.id in completed_ids:
                completed_count += 1
                completed_hours += task.estimated_hours
                phase_completed_hours[task.phase_num] = phase_completed_hours.get(task.phase_num, 0.0) + task.estimated_hours

        percentage = round((completed_hours / max(total_hours, 1.0)) * 100.0, 1) if total_hours > 0 else 0.0
        percentage = min(max(percentage, 0.0), 100.0)

        phase_progress: Dict[int, float] = {}
        for p in range(1, 5):
            tot = phase_total_hours.get(p, 0.0)
            comp = phase_completed_hours.get(p, 0.0)
            phase_progress[p] = round((comp / max(tot, 1.0)) * 100.0, 1) if tot > 0 else 0.0

        return RoadmapProgressState(
            career_id=roadmap.career_id,
            total_tasks=total_tasks,
            completed_tasks_count=completed_count,
            total_hours=round(total_hours, 1),
            completed_hours=round(completed_hours, 1),
            percentage=percentage,
            completed_task_ids=completed_ids,
            phase_progress=phase_progress
        )

    @classmethod
    def set_task_completed(cls, career_id: str, task_id: str, completed: bool) -> None:
        """Updates task completion state in SQLite repository."""
        RoadmapRepository.set_task_status(career_id, task_id, completed)

    @classmethod
    def reset_career_progress(cls, career_id: str) -> None:
        """Resets all roadmap progress for a career."""
        RoadmapRepository.reset_progress(career_id)
