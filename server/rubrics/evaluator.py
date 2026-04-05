# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Task definitions and graders for ATOM environment.
"""

from typing import Dict, Any, List, Optional
import math
from server.chemistry.engine import compute_properties, check_lipinski, check_alerts

class TaskDefinition:
    def __init__(self, task_id: int, difficulty: str, starting_scaffold: str, max_steps: int, tpp: Dict[str, Any]):
        self.task_id = task_id
        self.difficulty = difficulty
        self.starting_scaffold = starting_scaffold
        self.max_steps = max_steps
        self.tpp = tpp

# Define tasks
TASKS = {
    1: TaskDefinition(
        task_id=1,
        difficulty="Easy",
        starting_scaffold="c1ccccc1", # Benzene
        max_steps=5,
        tpp={"LogP": [2.5, 3.0]}
    ),
    2: TaskDefinition(
        task_id=2,
        difficulty="Medium",
        starting_scaffold="Cc1ccccc1", # Toluene
        max_steps=8,
        tpp={"LogP": [1.0, 2.5], "QED": [0.6, 1.0]} # Treating min threshold as a range up to max possible
    ),
    3: TaskDefinition(
        task_id=3,
        difficulty="Hard",
        starting_scaffold="c1cncnc1C(=O)NC", # Suboptimal kinase inhibitor (pyrimidine-based)
        max_steps=12,
        tpp={"LogP": [2.0, 3.5], "QED": [0.65, 1.0], "SA_Score": [1.0, 4.0], "MW": [300, 500], "Energy": [0.0, 150.0]}
    ),
    4: TaskDefinition(
        task_id=4,
        difficulty="Extreme",
        starting_scaffold="C", # Single Carbon atom
        max_steps=20,
        tpp={"LogP": [2.0, 4.0], "QED": [0.7, 1.0], "SA_Score": [1.0, 3.5], "MW": [250, 400], "Energy": [0.0, 100.0]}
    )
}

def gaussian_proximity(val: float, target_min: float, target_max: float, sigma: float = 1.0) -> float:
    """Calculates proximity score using a Gaussian function."""
    if target_min <= val <= target_max:
        return 1.0

    # Distance to nearest bound
    dist = min(abs(val - target_min), abs(val - target_max))
    return math.exp(-0.5 * (dist / sigma)**2)

def evaluate_target_adherence(props: Dict[str, float], tpp: Dict[str, Any]) -> float:
    """Evaluates how close properties are to TPP (Target Adherence: 40%)."""
    scores = []

    for prop, target_range in tpp.items():
        if prop in props:
            val = props[prop]
            t_min, t_max = target_range

            # Use different sigma based on property scale
            sigma = 1.0
            if prop == "MW": sigma = 50.0
            elif prop == "QED": sigma = 0.2
            elif prop == "LogP": sigma = 1.0
            elif prop == "SA_Score": sigma = 1.5
            elif prop == "Energy": sigma = 30.0

            scores.append(gaussian_proximity(val, t_min, t_max, sigma))

    if not scores: return 0.0
    return sum(scores) / len(scores)

class RubricEngine:
    """
    Trajectory-aware grading engine.
    """
    def __init__(self, task: TaskDefinition):
        self.task = task
        self.tpp = task.tpp
        self.max_steps = task.max_steps

    def score_trajectory(self, trajectory: List[Dict[str, Any]], final_mol: Any) -> float:
        """Scores the full trajectory returning a float between 0.0 and 1.0."""

        if not final_mol or not trajectory:
            return 0.0

        final_props = trajectory[-1].get("properties", {})
        if not final_props:
            final_props = compute_properties(final_mol)

        # 1. Target Adherence (40%)
        adherence_score = evaluate_target_adherence(final_props, self.tpp)

        # 2. Trajectory Quality (Monotonicity) (25%)
        # Here we approximate: did properties move towards target generally?
        traj_quality_score = self._compute_trajectory_quality(trajectory)

        # 3. Step Efficiency (15%)
        # Use exponential decay for step efficiency to avoid linear reward hacking
        # Early completion is highly rewarded; grinding out to max_steps approaches 0
        steps_taken = len(trajectory)
        efficiency_score = math.exp(-2.0 * (steps_taken / max(1, self.max_steps)))

        # 4. Chemical Validity (10%)
        alert_violations = check_alerts(final_mol)
        lipinski_violations = check_lipinski(final_mol)

        validity_score = 1.0
        if alert_violations:
            validity_score -= 0.5
        validity_score -= min(0.5, lipinski_violations * 0.1)
        validity_score = max(0.0, validity_score)

        # 5. Exploration Diversity (10%)
        # How many distinct fragment types were used?
        diversity_score = self._compute_diversity(trajectory)

        # Weighted sum
        final_score = (
            (adherence_score * 0.40) +
            (traj_quality_score * 0.25) +
            (efficiency_score * 0.15) +
            (validity_score * 0.10) +
            (diversity_score * 0.10)
        )

        return max(0.0, min(1.0, final_score))

    def _compute_trajectory_quality(self, trajectory: List[Dict[str, Any]]) -> float:
        """Advanced heuristic for trajectory monotonicity and area-under-curve."""
        if len(trajectory) <= 1: return 1.0

        adherences = [evaluate_target_adherence(step.get("properties", {}), self.tpp) for step in trajectory]

        # 1. Monotonicity Penalty
        inversions = 0
        max_adherence_so_far = adherences[0]

        for i in range(1, len(adherences)):
            if adherences[i] < adherences[i-1]:
                inversions += 1
            if adherences[i] > max_adherence_so_far:
                max_adherence_so_far = adherences[i]

        inversion_penalty = (inversions / len(adherences)) * 0.5

        # 2. Area Under the Curve (AUC) proxy
        # Higher average adherence during the trajectory means they reached good states early
        avg_adherence = sum(adherences) / len(adherences)

        # Combine: Reward high average adherence, penalize erratic reversals
        score = max(0.0, min(1.0, avg_adherence - inversion_penalty + 0.2)) # +0.2 baseline buffer
        return score

    def _compute_diversity(self, trajectory: List[Dict[str, Any]]) -> float:
        """Heuristic for exploration diversity."""
        fragments_used = set()
        for step in trajectory:
            frag = step.get("action", {}).get("fragment_name")
            if frag:
                fragments_used.add(frag)

        # If they used at least 2 distinct fragments (for multi-step), score well
        if not fragments_used: return 0.0
        return min(1.0, len(fragments_used) / 3.0)
