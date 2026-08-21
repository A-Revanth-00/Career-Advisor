from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List
from app.roadmap.roadmap_generator import Roadmap, RoadmapTask

@dataclass
class WeekAllocation:
    task: RoadmapTask
    allocated_hours: float
    is_split: bool = False
    part_info: str = ""

@dataclass
class WeekSchedule:
    week_number: int
    total_allocated_hours: float
    max_weekly_hours: float
    allocations: List[WeekAllocation] = field(default_factory=list)

@dataclass
class WeeklyPlan:
    career_id: str
    career_name: str
    weekly_hours_capacity: float
    total_estimated_hours: float
    total_estimated_weeks: int
    weeks: List[WeekSchedule] = field(default_factory=list)

class RoadmapPlanner:
    @classmethod
    def plan(cls, roadmap: Roadmap, hours_per_day: float, days_per_week: int) -> WeeklyPlan:
        """Schedules roadmap tasks into structured weeks according to student availability."""
        weekly_capacity = max(round(hours_per_day * days_per_week, 1), 1.0)
        
        weeks: List[WeekSchedule] = []
        current_week_num = 1
        current_week_allocations: List[WeekAllocation] = []
        current_week_used = 0.0

        for task in roadmap.tasks:
            remaining_task_hours = task.estimated_hours
            total_parts = 1
            if remaining_task_hours > weekly_capacity:
                total_parts = math.ceil(remaining_task_hours / weekly_capacity)
            part_idx = 1

            while remaining_task_hours > 0.001:
                available_in_current_week = round(weekly_capacity - current_week_used, 1)

                if available_in_current_week <= 0.01:
                    # Finalize current week and roll to next
                    weeks.append(WeekSchedule(
                        week_number=current_week_num,
                        total_allocated_hours=round(current_week_used, 1),
                        max_weekly_hours=weekly_capacity,
                        allocations=current_week_allocations
                    ))
                    current_week_num += 1
                    current_week_allocations = []
                    current_week_used = 0.0
                    available_in_current_week = weekly_capacity

                # Allocate up to available space
                to_allocate = min(remaining_task_hours, available_in_current_week)
                is_split = (to_allocate < task.estimated_hours)
                part_info = f"(Part {part_idx})" if is_split else ""

                current_week_allocations.append(WeekAllocation(
                    task=task,
                    allocated_hours=round(to_allocate, 1),
                    is_split=is_split,
                    part_info=part_info
                ))

                current_week_used += to_allocate
                remaining_task_hours -= to_allocate
                if is_split:
                    part_idx += 1

        # Append last week if has allocations
        if current_week_allocations:
            weeks.append(WeekSchedule(
                week_number=current_week_num,
                total_allocated_hours=round(current_week_used, 1),
                max_weekly_hours=weekly_capacity,
                allocations=current_week_allocations
            ))

        total_weeks = len(weeks)
        return WeeklyPlan(
            career_id=roadmap.career_id,
            career_name=roadmap.career_name,
            weekly_hours_capacity=weekly_capacity,
            total_estimated_hours=round(roadmap.total_hours, 1),
            total_estimated_weeks=total_weeks,
            weeks=weeks
        )
